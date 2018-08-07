from AbstractEngine import AbstractEngine
import DB
import Parsers
import os
import ReportGeneration
import Runners
import tempfile
from Errors import *
class MSGFPlusEngine(AbstractEngine):

    def list_multistep_search(self):
        rows = self.db_session.query(DB.MSGFPlusIterativeRun).all()
        return rows
    

    def multistep_search(self, mgf_name, msgfplus_index_names, msgfplus_search_options, multistep_search_name, fdr, postprocessing_object, modifications_name = None, memory = None):
        mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
        multistep_search_row = self.db_session.query(DB.MSGFPlusIterativeRun).filter_by(MSGFPlusIterativeRunName = multistep_search_name).first()
        msgf_location = self.executables['msgfplus']
        search_runner = Runners.MSGFPlusSearchRunner(msgfplus_search_options, msgf_location)
        if mgf_row and (multistep_search_row is None):
            mgf_location = os.path.abspath(os.path.join(self.project_path, mgf_row.MGFPath))
            #make sure the tide indices exist
            for name in msgfplus_index_names:
                index_row = self.db_session.query(DB.MSGFPlusIndex).filter_by(MSGFPlusIndexName = name).first()
                if index_row is None:
                    raise NoSuchMSGFPlusIndexError(name)
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
            for i in range(0, len(msgfplus_index_names)):
                index_name = msgfplus_index_names[i]
                if i > 0:
                    new_mgf_name = multistep_search_name + '_' + index_name + '_mgf'
                search_name = multistep_search_name + '_' + index_name
                filtered_name = search_name + '_msgf_filtered'
                self.run_search(new_mgf_name, index_name, modifications_name, search_runner, search_name, memory)
                """
                if use_percolator:
                    percolator_runner = Runners.PercolatorRunner(self.executables['crux'], 
                    postprocessing_object.percolator(search_name, 'msgfplus', 
                """
                postprocessing_object.filter_q_value_msgfplus(search_name, fdr, filtered_name)
                filtered_results.append((i, filtered_name))
                if i < len(msgfplus_index_names) - 1:
                    msgfplus_handler = ReportGeneration.MSGFPlusQValueHandler(search_name, fdr, self.project_path, self.db_session)
                    psms = msgfplus_handler.get_psms()
                    mgf_parser.remove_scans(list(set([x[0] for x in psms])))
                    temp_file = tempfile.NamedTemporaryFile(suffix='.mgf')
                    mgf_parser.write_modified_mgf(temp_file.name)
                    self.add_mgf_file(temp_file.name, multistep_search_name + '_' + msgfplus_index_names[i + 1] + '_mgf')
                    temp_file.close()
            rows = []
            iterativerun_row = DB.MSGFPlusIterativeRun(MSGFPlusIterativeRunName = multistep_search_name, fdr = str(fdr), num_steps = len(msgfplus_index_names), mgf = mgf_row)
            rows.append(iterativerun_row)
            for step, filtered_name in filtered_results:
                filtered_row = self.db_session.query(DB.FilteredSearchResult).filter_by(filteredSearchResultName = filtered_name).first()
                association_row = DB.MSGFPlusIterativeFilteredSearchAssociation(step = step)
                association_row.filteredsearch_result = filtered_row
                iterativerun_row.MSGFPlusIterativeFilteredSearchAssociations.append(association_row)
                rows.append(association_row)
            self.db_session.add_all(rows)
            self.db_session.commit()

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
            msgf_index_row = self.db_sesion.query(DB.MSGFPlusIndex).filter_by(MSGFPlusIndexName = index_name).first()
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

    def run_search(self, mgf_name, index_name, modifications_name, search_runner, search_name, memory=None):
        #modifications_name can be None if using default
        mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
        assert(mgf_row)
        index_row = self.db_session.query(DB.MSGFPlusIndex).filter_by(MSGFPlusIndexName=index_name).first()
        assert(index_row)
        modifications_row = None
        if modifications_name:
            modifications_row = self.db_session.query(DB.MSGFPlusModificationFile).filter_by(MSGFPlusModificationFileName=modifications_name).first()
            assert(modifications_row)
        search_row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName=search_name).first()
        assert(not search_row)
        output_directory = self.create_storage_directory('msgfplus_search_results')
        new_search_row = search_runner.run_search_create_row(mgf_row, index_row, modifications_row, output_directory,  self.project_path, search_name, memory)
        q_value_row = DB.MSGFPlusQValue(searchbase = new_search_row)
        self.db_session.add(new_search_row)
        self.db_session.add(q_value_row)
        self.db_session.commit()
        
            
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

    def create_index(self, set_type, set_name, index_runner, index_name, memory=None):
        #make sure there isn't an MSGFPlusIndex with the name index_name
        index_row = self.db_session.query(DB.MSGFPlusIndex).filter_by(MSGFPlusIndexName=index_name).first()
        assert(not index_row)
        storage_dir = self.create_storage_directory('msgfplus_indices')
        print('storage dir: ' + storage_dir)
        fasta_file_location, link_row, temp_files = self.create_fasta_for_indexing(set_type, set_name)
        row, fasta_name = index_runner.run_index_create_row(fasta_file_location, os.path.join(self.project_path, storage_dir), memory)
        if set_type == 'TargetSet':
            row.targetsets = [link_row]
        elif set_type == 'FilteredNetMHC':
            row.filteredNetMHCs = [link_row]
        elif set_type == 'PeptideList':
            row.peptidelists = [link_row]
        else:
            assert(False)
        row.MSGFPlusIndexName = index_name
        row.MSGFPlusIndexPath = os.path.join(storage_dir, fasta_name)
        self.db_session.add(row)
        self.db_session.commit()
    
