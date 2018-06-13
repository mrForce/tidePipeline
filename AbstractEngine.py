from abc import ABC, abstractmethod, ABCMeta
from Base import Base
import DB
import tempfile
from Errors import *
import subprocess
import os
class AbstractEngine(Base, metaclass=ABCMeta):
    @abstractmethod
    def list_search(self, mgf_name = None, index_name=None):
        pass
    @abstractmethod
    def run_search(self, mgf_name, index_name, search_runner, search_name, options):
        pass
    @abstractmethod
    def list_indices(self):
        pass
    @abstractmethod
    def create_index(self, set_type, set_name, index_runner, index_name):
        pass

    def create_fasta_for_indexing(self, set_type, set_name):
        """
        Returns a tuple of the form (fasta_file_location, link_row, temp_files)
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
                subprocess.call(['bash_scripts/join_peptides_to_fasta.sh', os.path.join(self.project_path, row.PeptideListPath), temp_fasta.name])
                temp_files.append(temp_fasta)
                fasta_file_location = temp_fasta.name
            else:
                raise NoSuchPeptideListError(set_name)
        else:
            assert(False)
        return (fasta_file_location, link_row, temp_files)

