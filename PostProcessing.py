from Base import Base
import DB
import ReportGeneration
from tabulate import tabulate
import collections
import Runners
import TargetSetSourceCount
import tempfile
from NetMHC import *
import os
from create_target_set import *
import uuid
from Errors import *

class PostProcessing(Base):
    def call_msgf2pin(self, msgf_search_name, percolator_location, msgf2pin_runner, fasta_files, decoy_pattern):
        msgf_row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName = msgf_search_name).first()
        assert(msgf_row is not None)
        msgf2pin_runner.runConversion(msgf_row.resultFilePath, percolator_location, fasta_files, decoy_pattern)
    def list_filtered_search_results(self, showIterative):
        headers = ['Name', 'Path', 'Q Value threshold', 'Search Name']
        rows = []
        for result in self.db_session.query(DB.FilteredSearchResult).all():
            name = result.filteredSearchResultName
            path = result.filteredSearchResultPath
            threshold = str(result.q_value_threshold)
            if result.QValue.searchbase is not None:
                if (showIterative and result.partOfIterativeSearch) or (not result.partOfIterativeSearch):
                    search_name = result.QValue.searchbase.SearchName
                    rows.append([name, path, threshold, search_name])
            else:
                print('Filtered search result searchbase is None: ' + name)
        for result in self.db_session.query(DB.MaxQuantSearch).all():
            search_name = result.SearchName
            path = result.Path
            threshold = str(result.fdr)
            rows.append(['MaxQuant', path, threshold, search_name])
        return tabulate(rows, headers=headers)
        
            
    def create_filtered_search_result(self, name, peptides, qvalue_row, threshold, partOfIterativeSearch = False):
        row = self.get_filtered_search_result_row(name)
        if row:
            raise FilteredSearchResultNameMustBeUniqueError(name)        
        filtered_filename = str(uuid.uuid4())
        while os.path.isfile(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename)) or os.path.isdir(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename)):
            filtered_filename = str(uuid.uuid4())
        with open(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename), 'w') as f:
            for peptide in peptides:
                f.write(peptide + '\n')
        filtered_row = DB.FilteredSearchResult(filteredSearchResultName = name, filteredSearchResultPath = os.path.join('FilteredSearchResult', filtered_filename), q_value_threshold = threshold, QValue = qvalue_row, partOfIterativeSearch = partOfIterativeSearch)
        self.db_session.add(filtered_row)
        self.db_session.commit()

    def filter_q_value_assign_confidence(self, assign_confidence_name, q_value_threshold, filtered_search_result_name, partOfIterativeSearch = False):
        assign_confidence_handler = ReportGeneration.AssignConfidenceHandler(assign_confidence_name, q_value_threshold, self.project_path, self.db_session, self.get_crux_executable_path())
        peptides = assign_confidence_handler.get_peptides()
        self.create_filtered_search_result(filtered_search_result_name, peptides, assign_confidence_handler.get_row() , q_value_threshold, partOfIterativeSearch)

    def filter_q_value_msgfplus(self, msgfplus_search_name, q_value_threshold, filtered_search_result_name, partOfIterativeSearch = False):
        msgfplus_handler = ReportGeneration.MSGFPlusQValueHandler(msgfplus_search_name, q_value_threshold, self.project_path, self.db_session)
        row = msgfplus_handler.get_row()
        peptides = msgfplus_handler.get_peptides()
        self.create_filtered_search_result(filtered_search_result_name, peptides, row, q_value_threshold, partOfIterativeSearch)

    def filter_q_value_percolator(self, percolator_name, q_value_threshold, filtered_search_result_name, partOfIterativeSearch = False):
        percolator_handler = ReportGeneration.PercolatorHandler(percolator_name, q_value_threshold, self.project_path, self.db_session, self.get_crux_executable_path())
        peptides = percolator_handler.get_peptides()
        self.create_filtered_search_result(filtered_search_result_name, peptides, percolator_handler.get_row(), q_value_threshold, partOfIterativeSearch)

    def get_filtered_search_result_row(self, name):
        return self.db_session.query(DB.FilteredSearchResult).filter_by(filteredSearchResultName = name).first()
    def get_tideiterativerun_row(self, name):
        return self.db_session.query(DB.TideIterativeRun).filter_by(TideIterativeRunName = name).first()
    def get_msgfplusiterativesearch_row(self, name):
        return self.db_session.query(DB.MSGFPlusIterativeRun).filter_by(MSGFPlusIterativeRunName = name).first()
    def verify_filtered_search_result(self, name):
        row = self.db_session.query(DB.FilteredSearchResult).filter_by(filteredSearchResultName = name).first()
        if row:
            return True
        else:
            return False
    def verify_maxquant_search(self, name):
        row = self.db_session.query(DB.MaxQuantSearch).filter_by(SearchName = name).first()
        if row:
            return True
        else:
            return False

    def count_sources(self, assign_confidence_name, q_val_threshold):
        row = self.get_assign_confidence(assign_confidence_name)
        if row:
            print('tide search')
            print(row.tideSearch)
            print('tide index')
            print(row.tideSearch.tideindex)
            print('filtered NetMHCs')
            print(row.tideSearch.tideindex.filteredNetMHCs)
            print('peptide lists')
            print(row.tideSearch.tideindex.peptidelists)
            print('target sets')
            print(row.tideSearch.tideindex.targetsets)
            target_set_row = row.tideSearch.tideindex.targetsets[0]
            q_val_column = 'tdc q-value'
            if row.estimation_method and len(row.estimation_method) > 0:
                q_val_column = row.estimation_method + ' q-value'
            handler = ReportGeneration.AssignConfidenceHandler(row, q_val_column, q_val_threshold, self.project_path, self.get_crux_executable_path())
            peptides = handler.getPeptides()
            
            return TargetSetSourceCount.count_sources(self.project_path, target_set_row, peptides)
    def get_assign_confidence(self, assign_confidence_name):
        return self.db_session.query(DB.AssignConfidence).filter_by(AssignConfidenceName = assign_confidence_name).first()
    def get_percolator(self, percolator_name):
        return self.db_session.query(DB.Percolator).filter_by(PercolatorName = percolator_name).first()


    def list_percolator(self, tide_search_name = None):
        filter_args = {}
        if tide_search_name:
            tide_search_row = self.db_session.query(DB.TideSearch).filter_by(SearchName = tide_search_name).first()
            if tide_search_row:
                filter_args['idSearch'] = tide_search_row.idSearch
            else:
                raise TideSearchRowDoesNotExistError(tide_search_name)
        if len(filter_args.keys()) > 0:
            return self.db_session.query(DB.Percolator).filter_by(**filter_args).all()
        else:
            return self.db_session.query(DB.Percolator).all()

    def list_assign_confidence(self, tide_search_name = None, estimation_method = None):
        filter_args = {}
        if tide_search_name:
            tide_search_row = self.db_session.query(DB.TideSearch).filter_by(SearchName = tide_search_name).first()
            if tide_search_row:
                filter_args['idSearch'] = tide_search_row.idSearch
            else:
                raise TideSearchRowDoesNotExistError(tide_search_name)
        if estimation_method:
            filter_args['estimation_method'] = estimation_method
        if len(filter_args.keys()) > 0:
            return self.db_session.query(DB.AssignConfidence).filter_by(**filter_args).all()
        else:
            return self.db_session.query(DB.AssignConfidence).all()
    
    def assign_confidence(self, tide_search_name, assign_confidence_runner, assign_confidence_name, partOfIterativeSearch = False):
        tide_search_row = self.db_session.query(DB.TideSearch).filter_by(SearchName = tide_search_name).first()
        assign_confidence_row = self.db_session.query(DB.AssignConfidence).filter_by(AssignConfidenceName = assign_confidence_name).first()
        if tide_search_row and (assign_confidence_row is None):
            #run_assign_confidence_create_row(target_path, output_directory_tide, output_directory_db, assign_confidence_name)
            target_path = os.path.join(self.project_path, tide_search_row.targetPath)
            output_directory_name = str(uuid.uuid4().hex)
            while os.path.isdir(os.path.join(self.project_path, 'assign_confidence_results', output_directory_name)):
                output_directory_name = str(uuid.uuid4().hex)
            output_directory_tide = os.path.join(self.project_path, 'assign_confidence_results', output_directory_name)
            output_directory_db = os.path.join('assign_confidence_results', output_directory_name)
            new_row = assign_confidence_runner.run_assign_confidence_create_row(target_path, output_directory_tide, output_directory_db, assign_confidence_name, tide_search_row, partOfIterativeSearch)
            self.db_session.add(new_row)
            self.db_session.commit()
        else:
            if tide_search_row is None:
                raise TideSearchRowDoesNotExistError(tide_search_name)
            if assign_confidence_row:
                raise AssignConfidenceNameMustBeUniqueError(assign_confidence_name)

    def percolator(self, search_name, search_type, percolator_runner, percolator_name, partOfIterativeSearch = False):
        search_row = None
        if search_type == 'tide':
            search_row = self.db_session.query(DB.TideSearch).filter_by(SearchName = search_name).first()
        elif search_type == 'msgfplus':
            search_row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName = search_name).first()
            assert(search_row.addFeatures == 1)
        percolator_row = self.db_session.query(DB.Percolator).filter_by(PercolatorName = percolator_name).first()
        if search_row and (percolator_row is None):            
            output_directory_name = str(uuid.uuid4().hex)
            while os.path.isdir(os.path.join(self.project_path, 'percolator_results', output_directory_name)):
                output_directory_name = str(uuid.uuid4().hex)
            output_directory_tide = os.path.join(self.project_path, 'percolator_results', output_directory_name)
            os.mkdir(output_directory_tide)
            output_directory_db = os.path.join('percolator_results', output_directory_name)
            if search_type == 'tide':
                target_path = os.path.join(self.project_path, search_row.targetPath)
            elif search_type == 'msgfplus':
                target_path = search_row.resultFilePath + '.pin'
                if not os.path.exists(target_path):
                    msgf2pin_runner = Runners.MSGF2PinRunner(self.executables['msgf2pin'], os.path.join(self.project_path, 'unimod.xml'))
                    head, tail = os.path.split(search_row.index.MSGFPlusIndexPath)
                    fasta_index = tail.rfind('.fasta')
                    new_tail = tail[:fasta_index] + '.revCat.fasta'
                    fasta_files = [os.path.join(self.project_path, head, new_tail)]
                    self.call_msgf2pin( search_name, target_path, msgf2pin_runner, fasta_files, 'XXX_')
            new_row = percolator_runner.run_percolator_create_row(target_path, output_directory_tide, output_directory_db, percolator_name, search_row, partOfIterativeSearch)
            self.db_session.add(new_row)
            self.db_session.commit()
        else:
            if search_row is None:
                if search_type == 'tide':
                    raise TideSearchRowDoesNotExistError(search_name)
                elif search_type == 'msgfplus':
                    raise MSGFPlusSearchRowDoesNotExistError(search_name)
            if percolator_row:
                raise PercolatorNameMustBeUniqueError(percolator_name)
    """
    Returns a list of NetMHC ranks.
    """
    def netmhc_rank_distribution(self, peptide_set_type, peptide_set_name, hla_names, netmhcpan = False):
        peptide_score_paths = []
        #add any tempfiles that will need to be cleaned up at end to this
        tempfiles = []
        if peptide_set_type == 'PeptideList':
            for hla in hla_names:
                netmhc_id, peptide_score_path = self._run_netmhc(peptide_set_name, hla, netmhcpan)
                peptide_score_paths.append(peptide_score_path)
        else:
            row = None
            if peptide_set_type == 'FilteredNetMHC':
                row = self.get_filtered_netmhc_row(peptide_set_name)
            if peptide_set_type == 'TargetSet':
                row = self.get_target_set_row(peptide_set_name)
            elif peptide_set_type == 'FilteredSearchResult':
                row = self.get_filtered_search_result_row(peptide_set_name)
            elif peptide_set_type == 'MaxQuantSearch':
                row = self.get_maxquant_search_row(peptide_set_name)
            elif peptide_set_type == 'TideIterativeSearch':
                row = self.get_tideiterativerun_row(peptide_set_name)
            elif args.CollectionType == 'MSGFPlusIterativeSearch':
                row = self.get_msgfplusiterativesearch_row(peptide_set_name)
            assert(row)
            peptides = row.get_peptides(self.project_path)
            for hla_name in hla_names:
                parsed_scores = tempfile.NamedTemporaryFile()
                peptide_score_path=  parsed_scores.name
                tempfiles.append(parsed_scores)
                peptide_score_paths.append((hla_name, peptide_score_path))
                with tempfile.TemporaryDirectory() as temp_dir:
                    peptide_file_path = os.path.join(temp_dir, 'peptides')
                    with open(os.path.join(temp_dir, 'peptides'), 'w') as f:
                        for peptide in peptides:
                            f.write(peptide + '\n')
                    netmhc_output_filepath = os.path.join(temp_dir, 'netmhcOutput')
                    call_netmhc(self.executables['netmhc'], hla_name, peptide_file_path, netmhc_output_filepath)
                    parse_netmhc(netmhc_output_filepath, peptide_score_path)

        """
        THIS IS WHERE I STOPPED! NEED TO FINISH HAVING MULTIPLE MHC alleles!
        """
        assert(len(peptide_score_paths) == len(hla_names))        
        #peptide_scores maps each peptide to a list of size len(hla_names), which by default contains 'NULL'.
        peptide_scores = collections.defaultdict(lambda: ['NULL']*len(hla_names))
        for hla, peptide_score_path in peptide_score_paths:
            hla_index = hla_names.index(hla)
            with open(peptide_score_path, 'r') as f:
                for line in f:
                    parts = line.split(',')
                    if len(parts) == 2:
                        peptide = parts[0].strip()
                        rank = parts[1].strip()
                        peptide_scores[peptide][hla_index] = rank
            
        for t in tempfiles:
            t.close()
        return peptide_scores
