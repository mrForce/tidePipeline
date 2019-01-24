from abc import ABC, abstractmethod, ABCMeta
from Base import Base
import DB
import tempfile
import BashScripts
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
    def create_index(self, set_type, set_name, index_runner, index_name, contaminant_names=[], *, netmhc_decoys = None):
        pass

    def create_fasta_for_indexing(self, set_type, set_name, contaminants=False):
        """
        Returns a tuple of the form (fasta_file_location, link_row, temp_files)
        """
        print('creating fasta for indexing')
        print('contaminants: ' + str(contaminants))
        fasta_file_location = ''
        temp_files = []
        link_row = None
        peptide_files = []
        fasta_files = []
        if contaminants:
            for x in contaminants:
                if set_type == 'FASTA':
                    fasta_files.append(os.path.join(self.project_path, x.fasta_file))
                else:
                    peptide_files.append(os.path.join(self.project_path, x.peptide_file))
                
            
        if set_type == 'TargetSet':
            target_set_name = set_name
            row = self.db_session.query(DB.TargetSet).filter_by(TargetSetName = target_set_name).first()
            if row:
                link_row = row
                fasta_file_location = os.path.join(self.project_path, row.TargetSetFASTAPath)
                fasta_files.append(fasta_file_location)
            else:
                raise NoSuchTargetSetError(set_name)
        elif set_type == 'FASTA':
            row = self.db_session.query(DB.FASTA).filter_by(Name = set_name).first()
            if row:
                link_row = row
                fasta_files.append(os.path.join(self.project_path, row.FASTAPath))
            else:
                raise NoSuchFASTAError(set_name)
        elif set_type == 'FilteredNetMHC':
            row = self.db_session.query(DB.FilteredNetMHC).filter_by(FilteredNetMHCName = set_name).first()
            if row:
                link_row = row
                peptide_files.append(row.filtered_path)
            else:
                raise NoSuchFilteredNetMHCError(set_name)
        elif set_type == 'PeptideList':
            row = self.db_session.query(DB.PeptideList).filter_by(peptideListName = set_name).first()
            if row:
                link_row = row
                peptide_files.append(row.PeptideListPath)
            else:
                raise NoSuchPeptideListError(set_name)
        else:
            assert(False)
        assert(len(peptide_files) > 0 or len(fasta_files) > 0)
        print('fasta files')
        print(fasta_files)
        print('peptide files')
        print(peptide_files)
        combined_peptide_file = None
        if len(peptide_files) > 1:
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt')
            subprocess.call(['bash_scripts/combine_and_uniq_files.sh'] + peptide_files + [temp_file.name])
            temp_files.append(temp_file)
            combined_peptide_file = temp_file.name
        elif len(peptide_files) > 0:
            combined_peptide_file = peptide_files[0]
        temp_fasta = tempfile.NamedTemporaryFile(mode='w', suffix='.fasta')
        temp_files.append(temp_fasta)
        if len(fasta_files) > 0:
            BashScripts.combine_files(fasta_files, temp_fasta.name)
        if combined_peptide_file:
            BashScripts.join_peptides_to_fasta(combined_peptide_file, temp_fasta.name)


        return (temp_fasta.name, link_row, temp_files)

