from AbstractEngine import AbstractEngine
import DB
import os
from tabulate import tabulate
import Runners
from Errors import *
class MaxQuantEngine(AbstractEngine):
    def list_search(self, raw_name = None):
        filter_args = {}
        if raw_name:
            raw_row = self.db_session.query(DB.RAWfile).filter_by(Name = raw_name).first()
            if raw_row:
                filter_args['idRAW'] = raw_row.idRAWfile
            else:
                raise RAWFileDoesNotExistError(raw_name)
        rows = []
        if len(filter_args.keys()) > 0:
            rows = self.db_session.query(DB.MaxQuantSearch).filter_by(**filter_args).all()
        else:
            rows = self.db_session.query(DB.MaxQuantSearch).all()
        tabulate_rows = []
        #not even going to bother with filterednetmhcs or targetsets or peptidelists for now
        headers = ['id', 'Search Name', 'RAW Name', 'Path', 'FDR']
        for row in rows:
            tabulate_rows.append([str(row.idSearch), row.SearchName, row.raw.RAWName, row.Path, row.fdr])
        return tabulate(tabulate_rows, headers=headers)

    def run_search(self, raw_name, param_file_name, search_runner, search_name, set_type, set_name, fdr):
        raw_row = self.db_session.query(DB.RAWfile).filter_by(RAWName = raw_name).first()
        assert(raw_row is not None)
        param_file_row = self.db_session.query(DB.MaxQuantParameterFile).filter_by(Name = param_file_name).first()
        assert(param_file_row is not None)
        search_row = self.db_session.query(DB.MaxQuantSearch).filter_by(SearchName = search_name).first()
        assert(search_row is None)
        output_directory = self.create_storage_directory('maxquant_search')
        fasta_file_location, link_row, temp_files = self.create_fasta_for_indexing(set_type, set_name)
        new_search_row = search_runner.run_search_create_row(raw_row, fasta_file_location, param_file_row, output_directory, self.project_path, search_name, fdr)
        if set_type == 'TargetSet':
            new_search_row.targetsets = [link_row]
        elif set_type == 'FilteredNetMHC':
            new_search_row.filteredNetMHCs = [link_row]
        elif set_type == 'PeptideList':
            new_search_row.peptidelists = [link_row]
        else:
            assert(False)
        self.db_session.add(new_search_row)
        self.db_session.commit()
        
            
    def list_indices(self):
        return None
    def create_index(self, set_type, set_name, index_runner, index_name, memory=None):
        return None
