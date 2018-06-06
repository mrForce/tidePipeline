from Base import Base
import tPipeDB
import ReportGeneration
import TargetSetSourceCount
import os
from create_target_set import *
import uuid
from Errors import *

class PostProcessing(Base):
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
        filtered_row = tPipeDB.FilteredSearchResult(filteredSearchResultName = name, filteredSearchResultPath = os.path.join('FilteredSearchResult', filtered_filename), q_value_threshold = threshold, QValue = qvalue_row)
        self.db_session.add(filtered_row)
        self.db_session.commit()

    def filter_q_value_assign_confidence(self, assign_confidence_name, q_value_threshold, filtered_search_result_name):
        row = self.get_assign_confidence(assign_confidence_name)
        q_val_column=  'tdc q-value'
        if row.estimation_method and len(row.estimation_method) > 0:
            q_val_column = row.estimation_method + ' q-value'
        handler = ReportGeneration.AssignConfidenceHandler(row, q_val_column, q_value_threshold, self.project_path)
        peptides = handler.getPeptides()
        filtered_filename = str(uuid.uuid4())
        while os.path.isfile(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename)) or os.path.isdir(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename)):
            filtered_filename = str(uuid.uuid4())
        with open(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename), 'w') as f:
            for peptide in peptides:
                f.write(peptide + '\n')
        filtered_row = tPipeDB.FilteredSearchResult(filteredSearchResultName = filtered_search_result_name, filteredSearchResultPath = os.path.join('FilteredSearchResult', filtered_filename), q_value_threshold = str(q_value_threshold), method='AssignConfidence')
        self.db_session.add(filtered_row)
        self.db_session.commit()

    def get_filtered_search_result_row(self, name):
        return self.db_session.query(tPipeDB.FilteredSearchResult).filter_by(filteredSearchResultName = name).first()
    
    def verify_filtered_search_result(self, name):
        row = self.db_session.query(tPipeDB.FilteredSearchResult).filter_by(filteredSearchResultName = name).first()
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
            print(row.tideSearch.tideIndex)
            print('filtered NetMHCs')
            print(row.tideSearch.tideIndex.filteredNetMHCs)
            print('peptide lists')
            print(row.tideSearch.tideIndex.peptidelists)
            print('target sets')
            print(row.tideSearch.tideIndex.targetsets)
            target_set_row = row.tideSearch.tideIndex.targetsets[0]
            q_val_column = 'tdc q-value'
            if row.estimation_method and len(row.estimation_method) > 0:
                q_val_column = row.estimation_method + ' q-value'
            handler = ReportGeneration.AssignConfidenceHandler(row, q_val_column, q_val_threshold, self.project_path)
            peptides = handler.getPeptides()
            
            return TargetSetSourceCount.count_sources(self.project_path, target_set_row, peptides)
    def get_assign_confidence(self, assign_confidence_name):
        return self.db_session.query(tPipeDB.AssignConfidence).filter_by(AssignConfidenceName = assign_confidence_name).first()
    def get_percolator(self, percolator_name):
        return self.db_session.query(tPipeDB.Percolator).filter_by(PercolatorName = percolator_name).first()
    def list_assign_confidence(self, tide_search_name = None, estimation_method = None):
        filter_args = {}
        if tide_search_name:
            tide_search_row = self.db_session.query(tPipeDB.TideSearch).filter_by(TideSearchName = tide_search_name).first()
            if tide_search_row:
                filter_args['idTideSearch'] = tide_search_row.idTideSearch
            else:
                raise TideSearchRowDoesNotExistError(tide_search_name)
        if estimation_method:
            filter_args['estimation_method'] = estimation_method
        if len(filter_args.keys()) > 0:
            return self.db_session.query(tPipeDB.AssignConfidence).filter_by(**filter_args).all()
        else:
            return self.db_session.query(tPipeDB.AssignConfidence).all()
        
    def assign_confidence(self, tide_search_name, assign_confidence_runner, assign_confidence_name):
        tide_search_row = self.db_session.query(tPipeDB.TideSearch).filter_by(TideSearchName = tide_search_name).first()
        assign_confidence_row = self.db_session.query(tPipeDB.AssignConfidence).filter_by(AssignConfidenceName = assign_confidence_name).first()
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
        tide_search_row = self.db_session.query(tPipeDB.TideSearch).filter_by(TideSearchName = tide_search_name).first()
        percolator_row = self.db_session.query(tPipeDB.Percolator).filter_by(PercolatorName = percolator_name).first()
        if tide_search_row and (percolator_row is None):
            target_path = os.path.join(self.project_path, tide_search_row.targetPath)
            output_directory_name = str(uuid.uuid4().hex)
            while os.path.isdir(os.path.join(self.project_path, 'percolator_results', output_directory_name)):
                output_directory_name = str(uuid.uuid4().hex)
            output_directory_tide = os.path.join(self.project_path, 'percolator_results', output_directory_name)
            output_directory_db = os.path.join('percolator_results', output_directory_name)
            new_row = percolator_runner.run_percolator_create_row(target_path, output_directory_tide, output_directory_db, percolator_name, tide_search_row)
            self.db_session.add(new_row)
            self.db_session.commit()
        else:
            if tide_search_row is None:
                raise TideSearchRowDoesNotExistError(tide_search_name)
            if percolator_row:
                raise PercolatorNameMustBeUniqueError(percolator_name)
