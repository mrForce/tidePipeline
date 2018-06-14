from AbstractEngine import AbstractEngine
import DB
import os
class MSGFPlusEngine(AbstractEngine):
    def list_search(self, mgf_name = None, index_name=None):
        pass
    def run_search(self, mgf_name, index_name, search_runner, search_name, options):
        mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
        assert(mgf_row)
        index_row = self.db_session.query(DB.MSGFPlusIndex).filter_by(MSGFPlusIndexName=index_name).first()
        assert(index_row)
        search_row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName=search_name).first()
        assert(not search_row)
        
        
            
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

    def create_index(self, set_type, set_name, index_runner, index_name):
        #make sure there isn't an MSGFPlusIndex with the name index_name
        index_row = self.db_session.query(DB.MSGFPlusIndex).filter_by(MSGFPlusIndexName=index_name).first()
        assert(not index_row)
        storage_dir = self.create_storage_directory('msgfplus_indices')
        print('storage dir: ' + storage_dir)
        fasta_file_location, link_row, temp_files = self.create_fasta_for_indexing(set_type, set_name)
        row, fasta_name = index_runner.run_index_create_row(fasta_file_location, os.path.join(self.project_path, storage_dir))
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
    
