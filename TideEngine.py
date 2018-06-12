from AbstractEngine import AbstractEngine
import tempfile
import DB
import subprocess
import uuid
import os
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
            tide_index_row = self.db_sesion.query(DB.TideIndex).filter_by(TideIndexName = tide_index_name).first()
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
        
    def run_search(self, mgf_name, tide_index_name, tide_search_runner, tide_search_name, options):
        print('in tide search function')
        mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
        tide_index_row = self.db_session.query(DB.TideIndex).filter_by(TideIndexName=tide_index_name).first()
        tide_search_row = self.db_session.query(DB.TideSearch).filter_by(TideSearchName=tide_search_name).first()
        if mgf_row and tide_index_row and (tide_search_row is None):
            directory_name = str(uuid.uuid4().hex)
            full_directory_path = os.path.join(self.project_path, 'tide_search_results', directory_name)
            while os.path.isfile(full_directory_path) or os.path.isdir(full_directory_path):
                directory_name = str(uuid.uuid4().hex)
                full_directory_path= os.path.join(self.project_path, 'tide_search_results', directory_name)
            row = tide_search_runner.run_search_create_row(mgf_row, tide_index_row, full_directory_path, os.path.join('tide_search_results', directory_name), options, self.project_path, tide_search_name)

            self.db_session.add(row)
            self.db_session.commit()
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



    def create_index(self, set_type, set_name, tide_index_runner, tide_index_name):
        """
        tide_index_runner is an instance of the TideIndexRunner class
        """
        fasta_file_location = ''
        temp_files = []
        link_row = None
        if set_type == 'TargetSet':
            target_set_name = set_name
            row = self.db_session.query(DB.TargetSet).filter_by(TargetSetName = target_set_name).first()
            if row:
                link_row = row
                fasta_file_location = os.path.join(self.project_path, row.TargetSetFASTAPath)
            else:
                raise NoSuchTargetSetError(set_name)
        elif set_type == 'FilteredNetMHC':
            row = self.db_session.query(DB.FilteredNetMHC).filter_by(FilteredNetMHCName = set_name).first()
            if row:
                link_row = row
                temp_fasta = tempfile.NamedTemporaryFile(mode='w')
                subprocess.call(['bash_scripts/join_peptides_to_fasta.sh', os.path.join(self.project_path, row.filtered_path), temp_fasta.name])
                temp_files.append(temp_fasta)
                fasta_file_location = temp_fasta.name
            else:
                raise NoSuchFilteredNetMHCError(set_name)
        elif set_type == 'PeptideList':
            row = self.db_session.query(DB.PeptideList).filter_by(peptideListName = set_name).first()
            if row:
                link_row = row
                temp_fasta = tempfile.NamedTemporaryFile(mode='w')
                subprocess.call(['bash_scripts/join_peptides_to_fasta.sh', os.path.join(self.project_path, row.PeptideListpath), temp_fasta.name])
                temp_files.append(temp_fasta)
                fasta_file_location = temp_fasta.name
            else:
                raise NoSuchPeptideListError(set_name)
        else:
            assert(False)
        output_directory_name = str(uuid.uuid4().hex)
        output_directory_path = os.path.join(self.project_path, 'tide_indices', output_directory_name)
        while os.path.isfile(output_directory_path) or os.path.isdir(output_directory_path):
            output_directory_name = str(uuid.uuid4().hex)
            output_directory_path = os.path.join(self.project_path, 'tide_indices', output_directory_name)
        
        row = tide_index_runner.run_index_create_row(fasta_file_location, output_directory_path, os.path.join('tide_indices', output_directory_name), 'index')
        for x in temp_files:
            x.close()
        row.TideIndexName = tide_index_name
        print('link row')
        print(link_row)
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
