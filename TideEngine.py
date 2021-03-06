from AbstractEngine import AbstractEngine
import tempfile
from Errors import *
import DB
import ReportGeneration
import subprocess
import Parsers
import uuid
import os
import Runners
import filecmp
class TideEngine(AbstractEngine):
    def list_search(self, mgf_name = None, tide_index_name = None):
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
        if tide_index_name:
            tide_index_row = self.db_session.query(DB.TideIndex).filter_by(TideIndexName = tide_index_name).first()
            if tide_index_row:
                filter_args['idTideIndex'] = tide_index_row.idTideIndex
            else:
                raise NoSuchTideIndexError(tide_index_name)
        rows = []
        if len(filter_args.keys()) > 0:
            rows = self.db_session.query(DB.TideSearch).filter_by(**filter_args).all()
        else:
            rows = self.db_session.query(DB.TideSearch).all()
        return rows

    def list_multistep_search(self):
        rows = self.db_session.query(DB.TideIterativeRun).all()
        return rows


    """
    peptide_identifier is either 'assign-confidence' or 'percolator'. 

    disable_contaminants_check is False by default. If it is set to True, then we don't check that every tide index is attached to the same ContaminantSets
    """
    def multistep_search(self, mgf_name, tide_index_names, search_param_file, multistep_search_name, fdr, peptide_identifier, param_file, postprocessing_object, *, disable_contaminants_check = False):
        
        assert(peptide_identifier in ['percolator', 'assign-confidence'])
        mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
        multistep_search_row = self.db_session.query(DB.TideIterativeRun).filter_by(IterativeSearchRunName = multistep_search_name).first()
        crux_location = self.executables['crux']
        print('tide index names: ' + ', '.join(tide_index_names))
        tide_index_row = self.db_session.query(DB.TideIndex).filter_by(TideIndexName = tide_index_names[0]).first()
        if tide_index_row is None:
            raise NoSuchTideIndexError(tide_index_names[0])
        contaminant_sets = {contaminant_set.idContaminantSet for contaminant_set in self.db_session.query(DB.TideIndex).filter_by(TideIndexName = tide_index_names[0]).first().get_contaminant_sets()}
        if mgf_row and (multistep_search_row is None):
            mgf_location = os.path.abspath(os.path.join(self.project_path, mgf_row.MGFPath))
            #make sure the tide indices exist
            for name in tide_index_names:
                tide_index_row = self.db_session.query(DB.TideIndex).filter_by(TideIndexName = name).first()
                if tide_index_row is None:
                    raise NoSuchTideIndexError(name)
                elif not disable_contaminants_check:
                    #I'm using the row ID, since I'm not sure how rows are compare to one another by sqlalchemy
                    temp_contaminant_sets = {contaminant_set.idContaminantSet for contaminant_set in tide_index_row.get_contaminant_sets()}
                    assert(len(temp_contaminant_sets) == len(contaminant_sets))
                    assert(len(temp_contaminant_sets & contaminant_sets) == len(contaminant_sets))

            """
            The name of each TideSearch row should be multistep_search_name + '_' + tide_index_name. 
            
            For each TideSearch, there will be a corresponding Percolator row. The name of this row should be multistep_search_name + '_' + tide_index_name + '_percolator'. 

            Each intermediate MGF file will be named multistep_search_name + '_' tide_index_name + '_mgf'

            We need to make sure each of these rows doesn't exist!
            """
            first_index = True
            for name in tide_index_names:
                new_search_name = multistep_search_name + '_' + name
                new_tide_search_row = self.db_session.query(DB.TideSearch).filter_by(SearchName = new_search_name).first()
                if not (new_tide_search_row is None):
                    raise TideSearchNameMustBeUniqueError(new_search_name)

                new_peptide_identifier_name = new_search_name + '_' + peptide_identifier
                if peptide_identifier == 'percolator':
                    new_peptide_identifier_row = self.db_session.query(DB.Percolator).filter_by(PercolatorName = new_peptide_identifier_name).first()
                    if not (new_peptide_identifier_row is None):
                        raise PercolatorNameMustBeUniqueError(new_peptide_identifier_name)
                elif peptide_identifier == 'assign-confidence':
                    new_peptide_identifier_row = self.db_session.query(DB.AssignConfidence).filter_by(AssignConfidenceName = new_peptide_identifier_name).first()
                    if not (new_peptide_identifier_row is None):
                        raise AssignConfidenceNameMustBeUniqueError(new_peptide_identifier_name)
                if not first_index:
                    new_mgf_name = multistep_search_name + '_' + name + '_mgf'
                    new_mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = new_mgf_name).first()
                    if not (new_mgf_row is None):
                        raise MGFNameMustBeUniqueError(new_mgf_name)
                else:
                     first_index = False   
                new_filtered_name = new_peptide_identifier_name + '_filtered'
                new_filtered_row = self.db_session.query(DB.FilteredSearchResult).filter_by(filteredSearchResultName = new_filtered_name).first()
                if not (new_filtered_row is None):
                    raise FilteredSearchResultNameMustBeUniqueError(new_filtered_name)
                

            """
            We're clear to start running the searches. We'll run the search on the mgf passed to us, then run Percolator, then extract the PSMs using PercolatorHandler from ReportGeneration. We'll extract the matched spectra from the MGF, creating a new MGF, and search it against the next tide index
            """
            new_mgf_name = mgf_name
            mgf_parser = Parsers.MGFParser(mgf_location)
            filtered_results = []
            search_names = []
            created_mgf_names = []
            for i in range(0, len(tide_index_names)):
                index_name = tide_index_names[i]
                index_row = self.db_session.query(DB.TideIndex).filter_by(TideIndexName = index_name).first()
                assert(not (index_row is None))
                need_search = True
                if i == 0:
                    rows_same_mgf_index = self.db_session.query(DB.TideSearch).filter_by(idTideIndex =  index_row.idIndex, idMGF = mgf_row.idMGFfile).all()
                    for row in rows_same_mgf_index:
                        if search_param_file and row.paramsPath:
                            if filecmp.cmp(search_param_file, os.path.join(self.project_path, row.paramsPath)):
                                #same index, mgf and parameter file. So we can re-use this search!
                                need_search = False
                                search_name = row.SearchName
                                print('We can re-use the Tide Search with name: ' + search_name)
                                break
                        elif (search_param_file is None) and (row.paramsPath is None):
                            need_search = False
                            search_name = row.SearchName
                            print('We can re-use the Tide Search with name: ' + search_name)
                            break
                
                if i > 0:
                    new_mgf_name = multistep_search_name + '_' + index_name + '_mgf'
                if need_search:
                    search_name = multistep_search_name + '_' + index_name
                peptide_identifier_name = multistep_search_name + '_' + index_name + '_' + peptide_identifier
                filtered_name = peptide_identifier_name + '_filtered'
                print('need search: ' + str(need_search))
                if need_search:
                    if search_param_file:
                        row = self.get_tide_search_parameter_file(search_param_file)
                        assert(row is not None)
                        search_runner = Runners.TideSearchRunner(crux_location, self.project_path, row)
                    else:
                        search_runner = Runners.TideSearchRunner(crux_location, self.project_path)
                    self.run_search(new_mgf_name, index_name, search_runner, search_name, None, True)
                    print('search name: ' + search_name)
                    search_names.append(search_name)
                if peptide_identifier == 'percolator':
                    #We ran the search, so now we need to call Percolator
                    if param_file:
                        row = self.get_percolator_parameter_file(param_file)
                        if row is None:
                            print('Invalid percolator parameter file name')
                            assert(False)
                        percolator_runner = Runners.PercolatorRunner(crux_location, self.project_path, row)
                    else:
                        percolator_runner = Runners.PercolatorRunner(crux_location, self.project_path)
                    print('search name: ' + search_name)
                    postprocessing_object.db_session = self.db_session
                    postprocessing_object.percolator(search_name, 'tide', percolator_runner, peptide_identifier_name, True)
                    postprocessing_object.filter_q_value_percolator(peptide_identifier_name, fdr, filtered_name, True)
                elif peptide_identifier == 'assign-confidence':
                    if param_file:
                        row = self.get_assign_confidence_parameter_file(param_file)
                        if row is None:
                            print('Not a valid assign confidence param file: ' + param_file)
                        assert(row)
                        assign_confidence_runner = Runners.AssignConfidenceRunner(crux_location, self.project_path, row)
                    else:
                        assign_confidence_runner = Runners.AssignConfidenceRunner(crux_location, self.project_path)
                    postprocessing_object.assign_confidence(search_name, assign_confidence_runner, peptide_identifier_name, True)
                    postprocessing_object.filter_q_value_assign_confidence(peptide_identifier_name, fdr, filtered_name, True)
                filtered_results.append((i, filtered_name))
                if i < len(tide_index_names) - 1:
                    if peptide_identifier == 'percolator':
                        #open up the Percolator results using PercolatorHandler
                        percolator_handler = ReportGeneration.PercolatorHandler(peptide_identifier_name, fdr, self.project_path, self.db_session, crux_location)
                        psms = percolator_handler.get_psms()
                    elif peptide_identifier == 'assign-confidence':
                        assign_confidence_handler = ReportGeneration.AssignConfidenceHandler(peptide_identifier_name, fdr, self.project_path, self.db_session, crux_location)
                        psms = assign_confidence_handler.get_psms()
                    mgf_parser.remove_scans(list(set([x[0] for x in psms])))
                    temp_file = tempfile.NamedTemporaryFile(suffix='.mgf')
                    mgf_parser.write_modified_mgf(temp_file.name)
                    self.add_mgf_file(temp_file.name, multistep_search_name + '_' + tide_index_names[i + 1] + '_mgf', True)
                    created_mgf_names.append(multistep_search_name + '_' + tide_index_names[i + 1] + '_mgf')
                    temp_file.close()
            rows = []
            iterativerun_row = DB.TideIterativeRun(IterativeSearchRunName = multistep_search_name, fdr = str(fdr), PeptideIdentifierName = peptide_identifier, num_steps = len(tide_index_names), mgf = mgf_row)
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
            
    def run_search(self, mgf_name, tide_index_name, tide_search_runner, tide_search_name, options=None, partOfIterativeSearch = False, *, threaded = None):
        #options doesn't do anything
        print('in tide search function')
        if threaded:
            assert(tide_search_runner.semaphore)
        else:
            assert(tide_search_runner.semaphore is None)
        mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
        tide_index_row = self.db_session.query(DB.TideIndex).filter_by(TideIndexName=tide_index_name).first()
        tide_search_row = self.db_session.query(DB.TideSearch).filter_by(SearchName=tide_search_name).first()
        if mgf_row and tide_index_row and (tide_search_row is None):
            directory_name = str(uuid.uuid4().hex)
            full_directory_path = os.path.join(self.project_path, 'tide_search_results', directory_name)
            while os.path.isfile(full_directory_path) or os.path.isdir(full_directory_path):
                directory_name = str(uuid.uuid4().hex)
                full_directory_path= os.path.join(self.project_path, 'tide_search_results', directory_name)
            if threaded:
                search_row, thread = tide_search_runner.run_search_create_row(mgf_row, tide_index_row, full_directory_path, os.path.join('tide_search_results', directory_name), tide_search_name, partOfIterativeSearch)
                return ([search_row], thread)
            else:
                search_row = tide_search_runner.run_search_create_row(mgf_row, tide_index_row, full_directory_path, os.path.join('tide_search_results', directory_name), tide_search_name, partOfIterativeSearch)
                return [search_row]
        else:
            if mgf_row is None:
                raise MGFRowDoesNotExistError(mgf_name)
            if tide_index_row is None:
                raise NoSuchTideIndexError(tide_index_name) 
            if tide_search_row:
                raise TideSearchNameMustBeUniqueError(tide_search_name)
    def list_indices(self):
        rows = self.db_session.query(DB.TideIndex).all()
        indices = []
        for row in rows:
            index = {'name': row.TideIndexName, 'id': str(row.idIndex), 'path':row.TideIndexPath, 'peptide_lists':[], 'filteredNetMHCs':[], 'target_sets': []}
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
    
    def create_index(self, set_type, set_name, tide_index_runner, tide_index_name, contaminant_names=[], *, netmhc_decoys = None, decoy_type = None):
        """
        tide_index_runner is an instance of the TideIndexRunner class
        """
        if decoy_type and netmhc_decoys:
            raise BothDecoyTypeAndNetMHCDecoysSpecifiedError()
        if decoy_type not in [None, 'random', 'tide_random', 'reverse', 'tide_reverse']:
            raise InvalidDecoyTypeError(decoy_type, [None, 'random', 'tide_random', 'reverse', 'tide_reverse'])
        contaminants = []
        print('contaminant names')
        print(contaminant_names)
        if contaminant_names:
            for name in contaminant_names:
                contaminantSet = self.db_session.query(DB.ContaminantSet).filter_by(contaminantSetName = name).first()
                assert(contaminantSet)
                contaminants.append(contaminantSet)
        fasta_file_location, link_row, temp_files  = self.create_fasta_for_indexing(set_type, set_name, contaminants)
        output_directory_name = str(uuid.uuid4().hex)
        output_directory_path = os.path.join(self.project_path, 'tide_indices', output_directory_name)
        while os.path.isfile(output_directory_path) or os.path.isdir(output_directory_path):
            output_directory_name = str(uuid.uuid4().hex)
            output_directory_path = os.path.join(self.project_path, 'tide_indices', output_directory_name)
        
        row = tide_index_runner.run_index_create_row(fasta_file_location, output_directory_path, os.path.join('tide_indices', output_directory_name), 'index', netmhc_decoys=netmhc_decoys, decoy_type = decoy_type)
        for x in temp_files:
            x.close()
        row.TideIndexName = tide_index_name
        print('link row')
        print(link_row)
        print('contamints')
        print(contaminants)
        if contaminants:
            row.contaminants = contaminants
        if set_type == 'TargetSet':
            row.targetsets = [link_row]
        elif set_type == 'FilteredNetMHC':
            row.filteredNetMHCs = [link_row]
        elif set_type == 'PeptideList':
            row.peptidelists = [link_row]
        else:
            assert(False)
        self.db_session.add(row)
        #self.db_session.commit()
