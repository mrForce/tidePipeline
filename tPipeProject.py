import tPipeDB
import os
from Bio import SeqIO
import glob
import re
import shutil
from fileFunctions import *
class Error(Exception):
    pass

class ProjectPathAlreadyExistsError(Error):
    def __init__(self, project_folder):
        self.message = 'Project folder ' + project_folder + ' already exists.'
    def __repr__(self):
        return self.message
class FASTAWithNameAlreadyExistsError(Error):
    def __init__(self, name):
        self.message = 'There\'s already a FASTA file with the name: ' + name + ' in the database'
    def __repr__(self):
        return self.message
class FileDoesNotExistError(Error):
    def __init__(self, filepath):
        self.message = 'File with path: ' + filepath + ' does not exist'
    def __repr__(self):
        return self.message
class FASTAWithNameDoesNotExistError(Error):
    def __init__(self, name):
        self.message = 'There is no FASTA entry with the name: ' + name

    def __repr__(self):
        return self.message
class HLAWithNameExistsError(Error):
    def __init__(self, hla_name):
        self.message = 'There is already an HLA with the name: ' + hla_name
    def __repr__(self):
        return self.message
class NoSuchSpeciesError(Error):
    def __init__(self, species_name):
        self.message = 'There is no species with the name: ' + species_name
    def __repr__(self):
        return self.message
class MultipleSpeciesWithSameNameError(Error):
    def __init__(self, species_name):
        self.message = 'There are multiple species with the name: ' + species_name
    def __repr__(self):
        return self.message
class NoSpeciesWithNameError(Error):
    def __init__(self, species_name):
        self.message = 'There are no species with the name: ' + species_name
    def __repr__(self):
        return self.message
class NoSpeciesWithIDError(Error):
    def __init__(self, species_id):
        self.message = 'There are no species with the ID: ' + str(species_id)
    def __repr__(self):
        return self.message
class MultipleSpeciesWithSameIDError(Error):
    def __init__(self, species_id):
        self.message = 'There are multiple species with the ID: ' + species_id
    def __repr__(self):
        return self.message

class NotProperFASTAFileError(Error):
    def __init__(self, path):
        self.message = 'The file at found at: ' + path + ' could not be parsed as a FASTA file'
    def __repr__(self):
        return self.message
class FASTAMissingError(Error):
    def __init__(self, fasta_id, fasta_name, path):
        self.message = 'The row in the FASTA table, with id: ' + str(fasta_id) + ' and name: ' + str(fasta_name) + ' points to a FASTA file with path: ' + path + ', but this file does not exist.'
    def __repr__(self):
        return self.message

class OperationsLockedError(Error):
    def __init__(self):
        self.message = 'The operation lock file (operation_lock) exists, so we cannot do anything with this project at the moment'
    def __repr__(self):
        return self.message
    
class Project:
    def __init__(self, project_path, command):
        self.project_path = project_path
        self.db_session = tPipeDB.init_session(os.path.join(project_path, 'database.db'))
        self.command = tPipeDB.Command(commandString = command)
        self.db_session.add(self.command)
        self.db_session.commit()

    
    def add_peptide_list(self, name, length, fasta_name):
        fasta_row = self.db_session.query(tPipeDB.FASTA).filter_by(Name=fasta_name).all()
        if len(fasta_row) == 0:
            raise FASTAWithNameDoesNotExistError(fasta_name)
        fasta_row = fasta_row[0]
        fasta_filename = os.path.split(fasta_row.FASTAPath)[1]
        peptide_filename = fasta_filename + '_' + str(length) + '.txt'
        peptide_list_path = os.path.join('peptides', peptide_filename)
        if not os.path.isfile(os.path.join(self.project_path, peptide_list_path)):                    
            peptides = extract_peptides(os.path.join(self.project_path, fasta_row.FASTAPath), length)        
            write_peptides(os.path.join(self.project_path, peptide_list_path), peptides)
        peptide_list = tPipeDB.PeptideList(peptideListName = name, length = length, fasta = fasta_row, PeptideListPath = peptide_list_path)
        self.db_session.add(peptide_list)
        self.db_session.commit()

    def list_files(self, folder):
        files_list = glob.glob(os.path.join(self.project_path, folder, '*'))
        return list(filter(lambda x: os.path.isfile(x), files_list))
    def list_fasta_files(self):
        return self.list_files('FASTA')
    def list_peptide_list_files(self):
        return self.list_files('peptides')
    def list_fasta_db(self):
        rows = self.db_session.query(tPipeDB.FASTA).all()
        fastas = []
        for row in rows:
            fasta = {'id': row.idFASTA, 'name': row.Name, 'comment': row.Comment, 'path': row.FASTAPath, 'peptide_lists': []}
            for pList in row.peptide_lists:
                fasta['peptide_lists'].append({'name': pList.peptideListName, 'length': pList.length})
            fastas.append(fasta)
        return fastas
    def add_species(self, species_name):
        species = tPipeDB.Species(SpeciesName = species_name)
        self.db_session.add(species)
    def validate_project_integrity(self, ignore_operation_lock = False):
        """
        Returns true if the project is valid. Otherwise it raises an error. That is:
        1) The lock file doesn't exist (operation_lock)
        3) All FASTA file paths in the FASTA table are found in the FASTA folder
        (and I'll add other criteria here as I expand the command set)
        
        """
        if (not ignore_operation_lock) and os.path.isfile(os.path.join(self.project_path, 'operation_lock')):
            raise OperationsLockedError()
        fasta_rows = self.db_session.query(tPipeDB.FASTA).all()
        for row in fasta_rows:
            path = row.FASTAPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                raise FASTAMissingError(row.idFASTA, row.Name, row.FASTAPath)
        return True
    def lock_operations(self):
        with open(os.path.join(self.project_path, 'operation_lock'), 'w') as f:
            pass
    def unlock_operations(self):
        os.remove(os.path.join(self.project_path, 'operation_lock'))
    def mark_invalid(self):
        with open(os.path.join(self.project_path, 'project_invalid'), 'w') as f:
            pass
    def remove_invalid_mark(self):
        os.remove(os.path.join(self.project_path, 'project_invalid'))
    def begin_command_session(self):
        """
        Validate project integrity, create operation lock
        """
        self.validate_project_integrity()
        current_place = os.getcwd()
        os.chdir(self.project_path)
        shutil.make_archive('backup', 'gztar')
        os.chdir(current_place)
        self.lock_operations()
    def end_command_session(self):
        """
        Validate project integrity (ignoring the operation lock). If project does not have integrity, then rollback project.

        If it does have integrity, then remove operation lock, and remove backup"""
        
        self.command.executionSuccess = 1
        
        self.db_session.commit()

        try:
            self.validate_project_integrity(ignore_operation_lock = True)
        except Error as e:
            #rollback
            print('Doing the operations caused the project to become invalid; here is the error')
            print(e)
            print('There is a backup file: ' + os.path.join(self.project_path, 'backup.tar.gz') + ' That you can use to revert the changes to bring the project into a valid state. Just unpack it. If you didn\'t do anything unusualy, then please file a bug report')
            sys.exit(1)
        else:
            self.unlock_operations()
            os.remove(os.path.join(self.project_path, 'backup.tar.gz'))
            
    def add_fasta_file(self, path, name, comment):
        """
        Steps:
        1) Validate that the file actually exists
        2) Make sure there isn't already a file with that name in the DB
        3) Validate that the file is actually a FASTA file
        4) Pick a name (the name in the filesystem, not the "name" column in the FASTA table) for the file, copy it over
        5) Add file to the database
        """
        if not os.path.isfile(path):
            raise FileDoesNotExistError(path)
        #step one done
        if len(self.db_session.query(tPipeDB.FASTA).filter_by(Name=name).all()) > 0:
            raise FASTAWithNameAlreadyExistsError(name)
        #step 2 done
        try:
            open_file = SeqIO.parse(path, 'fasta')
            for record in open_file:
                a = record.seq
        except:
            raise NotProperFASTAFileError(path)
        #step 3 done
        fasta_files = self.list_fasta_files()
        fasta_file_tails = [os.path.split(x)[1] for x in fasta_files]
        path_tail = os.path.split(path)[1]
        newpath= os.path.join('FASTA', path_tail)
        if path_tail in fasta_file_tails:
            max_version = 0
            """
            Let's say we add a FASTA file with the filename thing.fasta to our database 3 times.

            The first time, thing.fasta will be copied into the FASTA folder, and left with the filename "thing.fasta"
            The second time, a "-1" will be appended to the filename, to make "thing.fasta-1"
            The third time, a "-2" will be appended to the filename, to make "thing.fasta-2"
            """
            pattern = re.compile(re.escape(path_tail) + '-(?P<version>[0-9]*)')
            for tail in fasta_file_tails:
                match = pattern.match(tail)
                if match:
                    if len(match.group('version')) > 0:
                        version = int(match.group('version'))
                        if version > max_version:
                           max_version = version
            newpath = os.path.join('FASTA', path_tail + '-' + str(max_version + 1))
        shutil.copy(path, os.path.join(self.project_path, newpath))
        #did step 4
        fasta_record = tPipeDB.FASTA(Name = name, FASTAPath = newpath, Comment = comment)
        self.db_session.add(fasta_record)
        self.db_session.commit()
        return fasta_record.idFASTA
    def get_commands(self):
        commands = []
        for row in self.db_session.query(tPipeDB.Command):
            commands.append(row)
        return commands
    def get_species(self):
        species = []
        for row in self.db_session.query(tPipeDB.Species):
            hla = []
            for hla_row in row.hlas:
                hla.append(hla_row.HLAName)
            
            species.append({'id': row.idSpecies, 'name': row.SpeciesName, 'hla':hla  })
        return species

    def list_hla(self, species_name=None, species_id=None):
        if species_name:
            species_row = self.db_session.query(tPipeDB.Species).filter_by(SpeciesName=species_name).first()
            if species_row:
                species_id = species_row.idSpecies
            else:
                raise NoSuchSpeciesError(species_name)
        query = self.db_session.query(tPipeDB.HLA)
        if species_id:
            query = query.filter_by(species_id=species_id)
        rows = query.all()
        hlas = []
        for row in rows:
            hla = {'name': row.HLAName, 'id': str(row.idHLA)}
            if row.species:
                hla['species_id'] = str(row.species.idSpecies)
                hla['species_name'] = row.species.SpeciesName
            else:
                hla['species_id'] = 'None'
                hla['species_name'] = 'None'
            hlas.append(hla)
        return hlas
    def add_hla(self, hla_name, species, speciesIsID):
        species_rows = []
        if speciesIsID:
            species_rows = self.db_session.query(tPipeDB.Species).filter_by(idSpecies=species).all()
            if len(species_rows) == 0:
                raise NoSpeciesWithIDError(species)
            elif len(species_rows) > 1:
                raise MultipleSpeciesWithSameIDError(species)
        else:        
            species_rows = self.db_session.query(tPipeDB.Species).filter_by(SpeciesName=species).all()
            print(species_rows)
            print(len(species_rows))
            if len(species_rows) > 1:
                raise MultipleSpeciesWithSameNameError(species)
            elif len(species_rows) == 0:
                raise NoSpeciesWithNameError(species)
        hla_rows = self.db_session.query(tPipeDB.HLA).filter_by(HLAName = hla_name).all()
        if len(hla_rows) > 0:
            raise HLAWithNameExistsError(hla_name)
        hla = tPipeDB.HLA(HLAName = hla_name, species_id = species_rows[0].idSpecies)
        self.db_session.add(hla)
        self.db_session.commit()
        return hla.idHLA

        
        
        
    @staticmethod
    def createEmptyProject(project_path):
        if os.path.exists(project_path):
            raise ProjectPathAlreadyExistsError(project_path)
        else:
            os.mkdir(project_path)
            subfolders = ['FASTA', 'peptides', 'NetMHC', 'tide_indices', 'MGF', 'tide_search_results', 'percolator_results', 'misc']
            for subfolder in subfolders:
                os.mkdir(os.path.join(project_path, subfolder))
            return Project(project_path)



