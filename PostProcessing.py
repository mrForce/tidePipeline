import Base

class PostProcessing(Base):
    def assign_confidence_to_filtered_search_result(self, assign_confidence_name, q_value_threshold, filtered_search_result_name):
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
