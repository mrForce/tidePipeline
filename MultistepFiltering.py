from Base import Base
import DB
import ReportGeneration
from tabulate import tabulate
import TargetSetSourceCount
import os
from create_target_set import *
import uuid
from Errors import *

class MultistepFiltering(Base):

    def list_filtered_search_results(self):        
        headers = ['Name', 'Path', 'Q Value threshold', 'Search Name']
        rows = []
        for result in self.db_session.query(DB.FilteredSearchResult).all():
            name = result.filteredSearchResultName
            path = result.filteredSearchResultPath
            threshold = str(result.q_value_threshold)
            if result.QValue.searchbase is not None:
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
        
            
    def create_filtered_search_result(self, name, peptides, qvalue_row, threshold):
        row = self.get_filtered_search_result_row(name)
        if row:
            raise FilteredSearchResultNameMustBeUniqueError(name)        
        filtered_filename = str(uuid.uuid4())
        while os.path.isfile(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename)) or os.path.isdir(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename)):
            filtered_filename = str(uuid.uuid4())
        with open(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename), 'w') as f:
            for peptide in peptides:
                f.write(peptide + '\n')
        filtered_row = DB.FilteredSearchResult(filteredSearchResultName = name, filteredSearchResultPath = os.path.join('FilteredSearchResult', filtered_filename), q_value_threshold = threshold, QValue = qvalue_row)
        self.db_session.add(filtered_row)
        self.db_session.commit()

    def filter_q_value_assign_confidence(self, assign_confidence_name, q_value_threshold, filtered_search_result_name):
        assign_confidence_handler = ReportGeneration.AssignConfidenceHandler(assign_confidence_name, q_value_threshold, self.project_path, self.db_session, self.get_crux_executable_path())
        peptides = assign_confidence_handler.get_peptides()
        self.create_filtered_search_result(filtered_search_result_name, peptides, assign_confidence_handler.get_row() , q_value_threshold)

    def filter_q_value_msgfplus(self, msgfplus_search_name, q_value_threshold, filtered_search_result_name):
        msgfplus_handler = ReportGeneration.MSGFPlusQValueHandler(msgfplus_search_name, q_value_threshold, self.project_path, self.db_session)
        row = msgfplus_handler.get_row()
        peptides = msgfplus_handler.get_peptides()
        self.create_filtered_search_result(filtered_search_result_name, peptides, row, q_value_threshold)

    def filter_q_value_percolator(self, percolator_name, q_value_threshold, filtered_search_result_name):
        percolator_handler = ReportGeneration.PercolatorHandler(percolator_name, q_value_threshold, self.project_path, self.db_session, self.get_crux_executable_path())
        peptides = percolator_handler.get_peptides()
        self.create_filtered_search_result(filtered_search_result_name, peptides, percolator_handler.get_row(), q_value_threshold)

    def get_filtered_search_result_row(self, name):
        return self.db_session.query(DB.FilteredSearchResult).filter_by(filteredSearchResultName = name).first()
    
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
            peptides = handler.get_peptides()
            
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
    
    def assign_confidence(self, tide_search_name, assign_confidence_runner, assign_confidence_name):
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
            new_row = assign_confidence_runner.run_assign_confidence_create_row(target_path, output_directory_tide, output_directory_db, assign_confidence_name, tide_search_row)
            self.db_session.add(new_row)
            self.db_session.commit()
        else:
            if tide_search_row is None:
                raise TideSearchRowDoesNotExistError(tide_search_name)
            if assign_confidence_row:
                raise AssignConfidenceNameMustBeUniqueError(assign_confidence_name)

    def percolator(self, tide_search_name, percolator_runner, percolator_name):
        tide_search_row = self.db_session.query(DB.TideSearch).filter_by(SearchName = tide_search_name).first()
        percolator_row = self.db_session.query(DB.Percolator).filter_by(PercolatorName = percolator_name).first()
        if tide_search_row and (percolator_row is None):
            target_path = os.path.join(self.project_path, tide_search_row.targetPath)
            output_directory_name = str(uuid.uuid4().hex)
            while os.path.isdir(os.path.join(self.project_path, 'percolator_results', output_directory_name)):
                output_directory_name = str(uuid.uuid4().hex)
            output_directory_tide = os.path.join(self.project_path, 'percolator_results', output_directory_name)
            os.mkdir(output_directory_tide)
            output_directory_db = os.path.join('percolator_results', output_directory_name)
            new_row = percolator_runner.run_percolator_create_row(target_path, output_directory_tide, output_directory_db, percolator_name, tide_search_row)
            self.db_session.add(new_row)
            self.db_session.commit()
        else:
            if tide_search_row is None:
                raise TideSearchRowDoesNotExistError(tide_search_name)
            if percolator_row:
                raise PercolatorNameMustBeUniqueError(percolator_name)
