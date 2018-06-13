from AbstractEngine import AbstractEngine
import DB
class MSGFPlusEngine(AbstractEngine)
    def list_search(self, mgf_name = None, index_name=None):
        pass
    def run_search(self, mgf_name, index_name, search_runner, search_name, options):
        pass
    def list_indices(self):
        pass
    def create_index(self, set_type, set_name, index_runner, index_name):
        storage_dir = self.create_storage_directory('msgfplusindices')
        fasta_file_location, link_row, temp_files = self.create_fasta_for_indexing(set_type, set_name)
        row = index_runner.run_index_create_row(fasta_file_location, storage_dir)
        if set_type == 'TargetSet':
            row.targetsets = [link_row]
        elif set_type == 'FilteredNetMHC':
            row.filteredNetMHCs = [link_row]
        elif set_type == 'PeptideList':
            row.peptidelists = [link_row]
        else:
            assert(False)
        self.db_session.add(row)
        self.db_session.commit()
    
