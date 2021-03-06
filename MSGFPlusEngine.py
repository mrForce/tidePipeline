from AbstractEngine import AbstractEngine
import DB
import Parsers
import re
import os
import ReportGeneration
import fileFunctions
import Runners
import tempfile
from Errors import *
class MSGFPlusEngine(AbstractEngine):

    def list_multistep_search(self):
        rows = self.db_session.query(DB.MSGFPlusIterativeRun).all()
        return rows
    def get_msgfplus_search(self, name):
        row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName = name).first()
        if row is None:
            raise MSGFPlusSearchRowDoesNotExistError(name)
        return row

    def get_all_msgfplus_search(self):
        return self.db_session.query(DB.MSGFPlusSearch).all()

    
    def multistep_search(self, mgf_name, msgfplus_index_names, msgfplus_search_options, multistep_search_name, fdr, postprocessing_object, percolator_param_file=False, modifications_name = None, memory = None, *, disable_contaminants_check = False):
        """
        percolator_param_file is False if we want to use the Q-values calculated by MSGF+. percolator_param_file should be a string with the name of a Percolator parameter file if we want to use Percolator for calculating Q-values
        """
        mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
        multistep_search_row = self.db_session.query(DB.MSGFPlusIterativeRun).filter_by(IterativeSearchRunName = multistep_search_name).first()
        msgf_location = self.executables['msgfplus']
        contaminant_sets = {contaminant_set.idContaminantSet for contaminant_set in self.db_session.query(DB.MSGFPlusIndex).filter_by(MSGFPlusIndexName = msgfplus_index_names[0]).first().get_contaminant_sets()}
        search_runner = Runners.MSGFPlusSearchRunner(msgfplus_search_options, msgf_location)
        if mgf_row and (multistep_search_row is None):
            mgf_location = os.path.abspath(os.path.join(self.project_path, mgf_row.MGFPath))
            #make sure the tide indices exist
            for name in msgfplus_index_names:
                index_row = self.db_session.query(DB.MSGFPlusIndex).filter_by(MSGFPlusIndexName = name).first()
                if index_row is None:
                    raise NoSuchMSGFPlusIndexError(name)
                elif disable_contaminants_check:
                    temp_contaminant_sets = {contaminant_set.idContaminantSet for contaminant_set in index_row.get_contaminant_sets()}
                    assert(len(temp_contaminant_sets) == len(contaminant_sets))
                    assert(len(temp_contaminant_sets & contaminant_sets) == len(contaminant_sets))
            """
            The name of each MSGFPlusSearch row should be multistep_search_name + '_' + msgfplus_index_name. 
            

            Each intermediate MGF file will be named multistep_search_name + '_' msgfplus_index_name + '_mgf'

            We need to make sure each of these rows doesn't exist!
            """
            first_index = True
            for name in msgfplus_index_names:
                new_search_name = multistep_search_name + '_' + name
                new_msgfplus_search_row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName = new_search_name).first()
                if not (new_msgfplus_search_row is None):
                    raise MSGFPlusSearchNameMustBeUniqueError(new_search_name)
 
                new_filtered_name = new_search_name + '_msgfplus_filtered'
                new_filtered_row = self.db_session.query(DB.FilteredSearchResult).filter_by(filteredSearchResultName = new_filtered_name).first()
                if not (new_filtered_row is None):
                    raise FilteredSearchResultNameMustBeUniqueError(new_filtered_name)
                

            """
            We're clear to start running the searches. We'll run the search on the mgf passed to us, then run Percolator, then extract the PSMs using PercolatorHandler from ReportGeneration. We'll extract the matched spectra from the MGF, creating a new MGF, and search it against the next tide index
            """
            new_mgf_name = mgf_name
            mgf_parser = Parsers.MGFParser(mgf_location)
            filtered_results = []
            #search_names is a list of strings, each of which is the name of a search row used in the iterative search
            search_names = []
            #created_mgf_names is a list of strings, each of which is the name of an MGF row created by the iterative search
            created_mgf_names = []
            for i in range(0, len(msgfplus_index_names)):
                index_name = msgfplus_index_names[i]
                if i > 0:
                    new_mgf_name = multistep_search_name + '_' + index_name + '_mgf'
                search_name = multistep_search_name + '_' + index_name
                filtered_name = search_name + '_msgf_filtered'
                rows = self.run_search(new_mgf_name, index_name, modifications_name, search_runner, search_name, memory, True)
                for row in rows:
                    self.db_session.add(row)
                self.db_session.commit()
                search_names.append(search_name)
                
                percolator_name = None
                if percolator_param_file:
                    print('in percolator param file section')
                    
                    if not self.verify_row_existence(DB.PercolatorParameterFile.Name, percolator_param_file):
                        raise NoSuchPercolatorParameterFileError(percolator_param_file)
                    filtered_name = search_name + '_percolator_msgf_filtered'
                    row = self.get_percolator_parameter_file(percolator_param_file)
                    percolator_runner = Runners.PercolatorRunner(self.executables['crux'], self.project_path, row)
                    proposed_percolator_name = search_name + '_percolator'
                    percolator_names = self.get_column_values(DB.Percolator, 'PercolatorName')
                    percolator_name = fileFunctions.find_unique_name(percolator_names, proposed_percolator_name, re.compile(re.escape(proposed_percolator_name) + '-?(?P<version>\d*)'))
                    if self.verify_row_existence(DB.Percolator.PercolatorName, percolator_name):
                        raise DidNotFindUniquePercolatorNameError(percolator_name)
                    postprocessing_object.percolator(search_name, 'msgfplus', percolator_runner, percolator_name, True)
                    self.db_session.commit()
                    postprocessing_object.filter_q_value_percolator(percolator_name, fdr, filtered_name, True)
                else:
                    postprocessing_object.filter_q_value_msgfplus(search_name, fdr, filtered_name, True)
                self.db_session.commit()
                filtered_results.append((i, filtered_name))
                if i < len(msgfplus_index_names) - 1:
                    if percolator_param_file:
                        handler = ReportGeneration.PercolatorHandler(percolator_name, fdr, self.project_path, self.db_session, self.executables['crux'])
                    else:                            
                        handler = ReportGeneration.MSGFPlusQValueHandler(search_name, fdr, self.project_path, self.db_session)
                    psms = handler.get_psms()
                    mgf_parser.remove_scans(list(set([x[0] for x in psms])))
                    temp_file = tempfile.NamedTemporaryFile(suffix='.mgf')
                    mgf_parser.write_modified_mgf(temp_file.name)
                    self.add_mgf_file(temp_file.name, multistep_search_name + '_' + msgfplus_index_names[i + 1] + '_mgf', mgf_row.enzyme, mgf_row.fragmentationMethod, mgf_row.instrument, True)
                    created_mgf_names.append(multistep_search_name + '_' + msgfplus_index_names[i + 1] + '_mgf')
                    self.db_session.commit()
                    temp_file.close()
            rows = []
            iterativerun_row = DB.MSGFPlusIterativeRun(IterativeSearchRunName = multistep_search_name, fdr = str(fdr), num_steps = len(msgfplus_index_names), mgf = mgf_row)
            rows.append(iterativerun_row)
            for step, filtered_name in filtered_results:
                filtered_row = self.db_session.query(DB.FilteredSearchResult).filter_by(filteredSearchResultName = filtered_name).first()
                association_row = DB.IterativeFilteredSearchAssociation(step = step)
                association_row.filteredsearch_result = filtered_row
                iterativerun_row.IterativeFilteredSearchAssociations.append(association_row)
                rows.append(association_row)
            for search_name in search_names:
                search_row = self.db_session.query(DB.SearchBase).filter_by(SearchName = search_name).first()
                association_row = DB.IterativeRunSearchAssociation()
                association_row.search = search_row
                association_row.iterativerun = iterativerun_row
                rows.append(association_row)
            for mgf_name in created_mgf_names:
                mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
                association_row = DB.IterativeRunMGFAssociation()
                association_row.mgf = mgf_row
                association_row.iterativerun = iterativerun_row
                rows.append(association_row)
            self.db_session.add_all(rows)
            #self.db_session.commit()

    def list_search(self, mgf_name = None, index_name=None):
        """
        List the tide searches. You can specify an mgf name and/or tide index
        """
        filter_args = {}
        if mgf_name:
            mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
            if mgf_row:
                filter_args['idMGF'] = mgf_row.idMGFfile
            else:
                raise MGFRowDoesNotExistError(mgf_name)
        if index_name:
            msgf_index_row = self.db_session.query(DB.MSGFPlusIndex).filter_by(MSGFPlusIndexName = index_name).first()
            if msgf_index_row:
                filter_args['idMSGFPlusIndex'] = msgf_index_row.idMSGFPlusIndex
            else:
                raise NoSuchMSGFPlusIndexError(index_name)
        rows = []
        if len(filter_args.keys()) > 0:
            rows = self.db_session.query(DB.MSGFPlusSearch).filter_by(**filter_args).all()
        else:
            rows = self.db_session.query(DB.MSGFPlusSearch).all()
        return rows
        
    def run_training(self, mgf_name, search_name, training_name, training_runner, memory = None, *, commit=False):
        mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
        search_row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName = search_name).first()
        output_directory = self.create_storage_directory('msgf_params')
        training_row = training_runner.run_training_create_row(mgf_row, search_row, training_name, output_directory, memory)
        self.db_session.add(training_row)
        if commit:
            self.db_session.commit()

            
    def run_search(self, mgf_name, index_name, modifications_name, search_runner, search_name, memory=None, partOfIterativeSearch = False, tpm_file = False, tpm_id_type = False, uniprot_mapper = False,  *,  msgf_param_name = None, threaded=False):
        if threaded:
            assert(search_runner.semaphore)
        else:
            assert(search_runner.semaphore is None)
        #modifications_name can be None if using default        
        mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
        msgf_param_row = None
        if msgf_param_name:
            msgf_param_row = self.db_session.query(DB.MSGFPlusTrainingParams).filter_by(trainingName = msgf_param_name).first()
        assert(mgf_row)
        index_row = self.db_session.query(DB.MSGFPlusIndex).filter_by(MSGFPlusIndexName=index_name).first()
        assert(index_row)
        modifications_row = None
        if modifications_name:
            modifications_row = self.db_session.query(DB.MSGFPlusModificationFile).filter_by(MSGFPlusModificationFileName=modifications_name).first()
            assert(modifications_row)
        search_row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName=search_name).first()
        assert(not search_row)
        tpm_file_row = False
        if tpm_file:
            tpm_file_row = self.db_session.query(DB.TPMFile).filter_by(TPMName = tpm_file).first()
        uniprot_mapper_row = False
        if uniprot_mapper:
            uniprot_mapper_row = self.db_session.query(DB.UniprotMapper).filter_by(UniprotMapperName = uniprot_mapper).first()
        output_directory = self.create_storage_directory('msgfplus_search_results')
        if threaded:
            new_search_row, thread = search_runner.run_search_create_row(mgf_row, index_row, modifications_row, output_directory,  self.project_path, search_name, memory, partOfIterativeSearch, msgf_param_row, tpm_file_row, tpm_id_type, uniprot_mapper_row)
            q_value_row = DB.MSGFPlusQValue(searchbase = new_search_row)
            return ([new_search_row, q_value_row], thread)
        else:
            new_search_row = search_runner.run_search_create_row(mgf_row, index_row, modifications_row, output_directory,  self.project_path, search_name, memory, partOfIterativeSearch, msgf_param_row, tpm_file_row, tpm_id_type, uniprot_mapper_row)
            q_value_row = DB.MSGFPlusQValue(searchbase=new_search_row)
            return [new_search_row, q_value_row]
            
    def list_indices(self):
        rows = self.db_session.query(DB.MSGFPlusIndex).all()
        indices = []
        for row in rows:
            index = {'name': row.MSGFPlusIndexName, 'id': str(row.idIndex), 'path':row.MSGFPlusIndexPath, 'peptide_lists':[], 'filteredNetMHCs':[], 'target_sets': []}
            for r in row.targetsets:
                index['target_sets'].append({'name': r.TargetSetName})
            for l in row.peptidelists:
                index['peptide_lists'].append({'name': l.peptideListName, 'length': str(l.length), 'fasta_name': l.fasta.Name})
            for n in row.filteredNetMHCs:
                netmhc = self.db_session.query(DB.NetMHC).filter_by(idNetMHC=n.idNetMHC).first()
                if netmhc:
                    peptide_list_row = self.db_session.query(DB.PeptideList).filter_by(idPeptideList=netmhc.peptidelistID).first()
                    hla_row = self.db_session.query(DB.HLA).filter_by(idHLA=netmhc.idHLA).first()
                    if peptide_list_row and hla_row:
                        index['filteredNetMHCs'].append({'hla': hla_row.HLAName, 'name': peptide_list_row.peptideListName, 'length': str(peptide_list_row.length), 'fasta_name': peptide_list_row.fasta.Name})
            indices.append(index)
        return indices

    def create_index(self, set_type, set_name, index_runner, index_name, contaminant_names = [], memory=None, *, netmhc_decoys = None, decoy_type = None):
        contaminants = []
        print('contaminants: ' + ', '.join(contaminant_names))
        if contaminant_names:
            for name in contaminant_names:
                print('contaminant: ' + name)
                contaminantSet = self.db_session.query(DB.ContaminantSet).filter_by(contaminantSetName = name).first()
                assert(contaminantSet)
                contaminants.append(contaminantSet)

        #make sure there isn't an MSGFPlusIndex with the name index_name
        index_row = self.db_session.query(DB.MSGFPlusIndex).filter_by(MSGFPlusIndexName=index_name).first()
        assert(not index_row)
        storage_dir = self.create_storage_directory('msgfplus_indices')
        print('storage dir: ' + storage_dir)
        fasta_file_location = None
        link_row = None
        """
        if set_type == 'FASTA':
            link_row = self.get_fasta_row(set_name)
            fasta_file_location = os.path.join(self.project_path, link_row.FASTAPath)
        else:
"""
        fasta_file_location, link_row, temp_files = self.create_fasta_for_indexing(set_type, set_name, contaminants)
        
        row, fasta_name = index_runner.run_index_create_row(fasta_file_location, os.path.join(self.project_path, storage_dir), self.project_path, memory, netmhc_decoys=netmhc_decoys, decoy_type=decoy_type)
        print('fasta name: ' + fasta_name)
        print('storage dir: ' + storage_dir)
        print('set type: ' + set_type)
        if contaminants:
            row.contaminants = contaminants
        if set_type == 'TargetSet':
            row.targetsets.append(link_row)
        elif set_type == 'FilteredNetMHC':
            row.filteredNetMHCs.append(link_row)
        elif set_type == 'PeptideList':
            row.peptidelists.append(link_row)
        elif set_type == 'FASTA':
            print('going to link MSGF+ index to fasta: ')
            print(link_row)
            row.fasta.append(link_row)
        else:
            assert(False)
        row.MSGFPlusIndexName = index_name
        row.MSGFPlusIndexPath = os.path.join(storage_dir, fasta_name)
        self.db_session.add(row)
        print('session state: ')
        for x in self.db_session:
            print(x)
        print('done printing session state')
        #self.db_session.commit()
    
