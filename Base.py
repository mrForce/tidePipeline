import tPipeDB
from create_target_set import *
import sys
import tempfile
import os
from Bio import SeqIO
from NetMHC import *
import glob
import re
import shutil
import uuid
from fileFunctions import *
from datetime import datetime
import json
import TargetSetSourceCount
import ReportGeneration

from Errors import *
from Runners import *

    
    


class Base:
    def __init__(self, project_path, command):
        if os.path.isfile('reminder.txt'):
            subprocess.call(['cat', 'reminder.txt'])
        self.project_path = project_path
        print('project path: ' + project_path)
        self.db_session = tPipeDB.init_session(os.path.join(project_path, 'database.db'))
        self.command = tPipeDB.Command(commandString = command)
        self.db_session.add(self.command)
        self.db_session.commit()


        
        
    def get_filtered_netmhc_row(self, name):
        return self.db_session.query(tPipeDB.FilteredNetMHC).filter_by(FilteredNetMHCName = name).first()

    def get_target_set_row(self, name):
        return self.db_session.query(tPipeDB.TargetSet).filter_by(TargetSetName = name).first()
    def get_peptide_list_row(self, name):
        return self.db_session.query(tPipeDB.PeptideList).filter_by(peptideListName = name).first()
    def add_targetset(self, netmhc_filter_names, peptide_list_names, target_set_name):
        #need to create lists of the form [(name, location)...]
        netmhc_filter_locations = []
        peptide_list_locations = []
        if netmhc_filter_names:
            for name in netmhc_filter_names:
                row  = self.db_session.query(tPipeDB.FilteredNetMHC).filter_by(FilteredNetMHCName = name).first()
                if row:
                    location = os.path.join(self.project_path, row.filtered_path)
                    netmhc_filter_locations.append((name, location))
                else:
                    raise NoSuchFilteredNetMHCError(name)
        if peptide_list_names:
            for name in peptide_list_names:
                row = self.db_session.query(tPipeDB.PeptideList).filter_by(peptideListName = name).first()
                if row:
                    location = os.path.join(self.project_path, row.PeptideListPath)
                    peptide_list_locations.append((name, location))
                else:
                    raise NoSuchPeptideListError(name)
        if self.db_session.query(tPipeDB.TargetSet).filter_by(TargetSetName = target_set_name).first():
            raise TargetSetNameMustBeUniqueError(target_set_name)
        
        output_folder = str(uuid.uuid4())
        while os.path.isdir(os.path.join(self.project_path, 'TargetSet', output_folder)) or os.path.isfile(os.path.join(self.project_path, 'TargetSet', output_folder)):
            output_folder = str(uuid.uuid4())
        os.mkdir(os.path.join(self.project_path, 'TargetSet', output_folder))
        output_fasta_location = os.path.join(self.project_path, 'TargetSet', output_folder, 'targets.fasta')
        output_json_location = os.path.join(self.project_path, 'TargetSet', output_folder, 'sources.json')

        source_id_map = create_target_set(netmhc_filter_locations, peptide_list_locations, output_fasta_location, output_json_location)
        target_set_row = tPipeDB.TargetSet(TargetSetFASTAPath = os.path.join('TargetSet', output_folder, 'targets.fasta'), PeptideSourceMapPath=os.path.join('TargetSet', output_folder, 'sources.json'), SourceIDMap=json.dumps(source_id_map), TargetSetName = target_set_name)
        self.db_session.add(target_set_row)
        self.db_session.commit()
    def verify_filtered_netMHC(self, name):
        if self.db_session.query(tPipeDB.FilteredNetMHC).filter_by(FilteredNetMHCName = name).first():
            return True
        else:
            return False
    def verify_target_set(self, name):
        if self.db_session.query(tPipeDB.TargetSet).filter_by(TargetSetName = name).first():
            return True
        else:
            return False

    def add_mgf_file(self, path, name):
        row = self.db_session.query(tPipeDB.MGFfile).filter_by(MGFName = name).first()
        if row:
            raise MGFNameMustBeUniqueError(name)
        else:
            newpath = self.copy_file('MGF', path)
            mgf_record = tPipeDB.MGFfile(MGFName = name, MGFPath = newpath)
            self.db_session.add(mgf_record)
            self.db_session.commit()
            return mgf_record.idMGFfile    

    def verify_peptide_list(self, peptide_list_name):
        row = self.db_session.query(tPipeDB.PeptideList).filter_by(peptideListName = peptide_list_name).first()
        if row is None:
            return False
        else:
            return True

    def verify_hla(self, hla):
        row = self.db_session.query(tPipeDB.HLA).filter_by(HLAName = hla).first()
        if row is None:
            return False
        else:
            return True

    def run_netmhc(self, peptide_list_name, hla, rank_cutoff, filtered_name, netmhcpan = False):
        idNetMHC, pep_score_path = self._run_netmhc(peptide_list_name, hla, netmhcpan)
        print('idNetMHC: ' + str(idNetMHC))
        
        row = self.db_session.query(tPipeDB.FilteredNetMHC).filter_by(idNetMHC = idNetMHC, RankCutoff = rank_cutoff).first()
        #to be clear, this means that 
        if row is None:
            file_name = str(uuid.uuid4())
            while os.path.isfile(os.path.join(self.project_path, 'FilteredNetMHC', file_name)) or os.path.isdir(os.path.join(self.project_path, 'FilteredNetMHC', file_name)):
                file_name = str(uuid.uuid4())
            print('current place: ' + os.getcwd())
            output_path = os.path.join(self.project_path, 'FilteredNetMHC', file_name)
            input_path = os.path.join(self.project_path, pep_score_path)
            with open(input_path, 'r') as f:
                with open(output_path, 'w') as g:
                    for line in f:
                        parts = line.split(',')
                        if len(parts) == 2:
                            peptide = parts[0].strip()
                            rank = float(parts[1])
                            if rank <= rank_cutoff:
                                g.write(peptide + '\n')
            
            
            filtered_row = tPipeDB.FilteredNetMHC(idNetMHC = idNetMHC, RankCutoff = rank_cutoff, FilteredNetMHCName = filtered_name, filtered_path = os.path.join('FilteredNetMHC', file_name))
            self.db_session.add(filtered_row)
            self.db_session.commit()
            
                
        
    


    def add_peptide_list(self, name, length, fasta_name):
        fasta_row = self.db_session.query(tPipeDB.FASTA).filter_by(Name=fasta_name).first()
        if fasta_row is None:
            raise FASTAWithNameDoesNotExistError(fasta_name)
        print('length:')
        print(length)
        peptide_row = self.db_session.query(tPipeDB.PeptideList).filter_by(length = length, fasta = fasta_row).first()
        if peptide_row is None:
            fasta_filename = os.path.split(fasta_row.FASTAPath)[1]
            peptide_filename = fasta_filename + '_' + str(length) + '.txt'
            peptide_list_path = os.path.join('peptides', peptide_filename)
            if not os.path.isfile(os.path.join(self.project_path, peptide_list_path)):
                peptides = extract_peptides(os.path.join(self.project_path, fasta_row.FASTAPath), length)
                write_peptides(os.path.join(self.project_path, peptide_list_path), peptides)
            peptide_list = tPipeDB.PeptideList(peptideListName = name, length = length, fasta = fasta_row, PeptideListPath = peptide_list_path)
            self.db_session.add(peptide_list)
            self.db_session.commit()
    def _run_netmhc(self, peptide_list_name, hla_name, netmhcpan = False):
        """
        This first checks if there's already a in NetMHC for the given peptide list and HLA. If there is, then it just returns a tuple of the form: (idNetMHC, PeptideScorePath)
        
        If there isn't, then it runs NetMHC, inserts a row into the table, and returns (idNetMHC, PeptideScorePath)               
        """
        peptide_list_row = self.db_session.query(tPipeDB.PeptideList).filter_by(peptideListName=peptide_list_name).first()
        if peptide_list_row is None:
            raise NoSuchPeptideListError(peptide_list_name)
        hla_row = self.db_session.query(tPipeDB.HLA).filter_by(HLAName=hla_name).first()
        if hla_row is None:
            raise NoSuchHLAError(hla_name)
        netmhc_row = self.db_session.query(tPipeDB.NetMHC).filter_by(peptidelistID=peptide_list_row.idPeptideList, idHLA=hla_row.idHLA).first()
        if netmhc_row:
            return (netmhc_row.idNetMHC, netmhc_row.PeptideScorePath)
        else:
            netmhc_output_filename = str(uuid.uuid4().hex)
            while os.path.isfile(os.path.join(self.project_path, 'NetMHC', netmhc_output_filename)) or os.path.isfile(os.path.join(self.project_path, 'NetMHC', netmhc_output_filename, '-parsed')):
                netmhc_output_filename = str(uuid.uuid4().hex)
            call_netmhc(hla_name, os.path.join(self.project_path, peptide_list_row.PeptideListPath), os.path.join(self.project_path, 'NetMHC', netmhc_output_filename), netmhcpan)
            parse_netmhc(os.path.join(self.project_path, 'NetMHC', netmhc_output_filename), os.path.join(self.project_path, 'NetMHC', netmhc_output_filename + '-parsed'))
            netmhc_row = tPipeDB.NetMHC(peptidelistID=peptide_list_row.idPeptideList, idHLA = hla_row.idHLA, NetMHCOutputPath=os.path.join('NetMHC', netmhc_output_filename), PeptideScorePath = os.path.join('NetMHC', netmhc_output_filename + '-parsed'))
            self.db_session.add(netmhc_row)
            self.db_session.commit()
            return (netmhc_row.idNetMHC, netmhc_row.PeptideScorePath)


    def list_peptide_lists(self):
        peptide_lists = []
        peptide_list_rows = self.db_session.query(tPipeDB.PeptideList).all()
        for row in peptide_list_rows:
            peptide_list = {'id': row.idPeptideList, 'name': row.peptideListName, 'FASTAName': row.fasta.Name, 'FASTAPath': row.fasta.FASTAPath, 'length': int(row.length), 'path': row.PeptideListPath}
            peptide_lists.append(peptide_list)
        return peptide_lists
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
    def list_mgf_db(self):
        rows = self.db_session.query(tPipeDB.MGFfile).all()        
        mgfs = []
        for row in rows:
            mgf = {'id': row.idMGFfile, 'name': row.MGFName, 'path': row.MGFPath}
            mgfs.append(mgf)
        return mgfs

    def add_species(self, species_name):
        species = tPipeDB.Species(SpeciesName = species_name)
        self.db_session.add(species)
    def validate_project_integrity(self, ignore_operation_lock = False):
        """
        Returns true if the project is valid. Otherwise it raises an error. That is:
        1) The lock file doesn't exist (operation_lock)
        2) All FASTA file paths in the FASTA table are found in the FASTA folder
        (and I'll add other criteria here as I expand the command set)
        3) All peptide list files are present
        """
        print('going to validate project integrity')
        print('current time: ' + str(datetime.now().time()))
        #if (not ignore_operation_lock) and os.path.isfile(os.path.join(self.project_path, 'operation_lock')):
        #    raise OperationsLockedError()
        print('going to check fasta rows')
        fasta_rows = self.db_session.query(tPipeDB.FASTA).all()
        for row in fasta_rows:
            path = row.FASTAPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                raise FASTAMissingError(row.idFASTA, row.Name, row.FASTAPath)
        print('going to check peptide list rows')
        peptide_list_rows = self.db_session.query(tPipeDB.PeptideList).all()
        for row in peptide_list_rows:
            path = row.PeptideListPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                raise PeptideListFileMissingError(row.idPeptideList, row.peptideListName, row.PeptideListPath)
        print('going to check mgf rows')
        mgf_rows = self.db_session.query(tPipeDB.MGFfile).all()
        for row in mgf_rows:
            path = row.MGFPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                raise MGFFileMissingError(row.idMGFfile, row.MGFName, row.MGFPath)
        print('done validating project integrity')
        print('current time: ' + str(datetime.now().time()))
        return True
    def lock_operations(self):
        pass
        #with open(os.path.join(self.project_path, 'operation_lock'), 'w') as f:
        #    pass
    def unlock_operations(self):
        pass
        #os.remove(os.path.join(self.project_path, 'operation_lock'))
        
    def mark_invalid(self):
        with open(os.path.join(self.project_path, 'project_invalid'), 'w') as f:
            pass
    def remove_invalid_mark(self):
        os.remove(os.path.join(self.project_path, 'project_invalid'))
    def begin_command_session(self, validate=True):
        """
        Validate project integrity, create operation lock
        """
        if validate:
            self.validate_project_integrity()
            current_place = os.getcwd()
            os.chdir(self.project_path)
            #shutil.make_archive('backup', 'gztar')
            #just copy the database.db file
            shutil.copyfile('database.db', 'database.db.backup')
            os.chdir(current_place)
            self.lock_operations()
    def end_command_session(self, validate=True):
        """
        Validate project integrity (ignoring the operation lock). If project does not have integrity, then rollback project.

        If it does have integrity, then remove operation lock, and remove backup"""
        
        self.command.executionSuccess = 1
        
        self.db_session.commit()
        if validate:
            try:
                self.validate_project_integrity(ignore_operation_lock = True)
            except Error as e:
                #rollback
                print('Doing the operations caused the project to become invalid; here is the error')
                print(sys.exc_info()[0])                
                sys.exit(1)
            else:
                self.unlock_operations()
                #os.remove(os.path.join(self.project_path, 'backup.tar.gz'))
    def copy_file(self, subfolder, path):
        files = self.list_files(subfolder)
        tails = [os.path.split(x)[1] for x in files]
        path_tail = os.path.split(path)[1]
        newpath= os.path.join(subfolder, path_tail)
        if path_tail in tails:
            max_version = 0
            """
            Let's say we add a FASTA file with the filename thing.fasta to our database 3 times.

            The first time, thing.fasta will be copied into the FASTA folder, and left with the filename "thing.fasta"
            The second time, a "-1" will be appended to the filename, to make "thing.fasta-1"
            The third time, a "-2" will be appended to the filename, to make "thing.fasta-2"
            """
            pattern = re.compile(re.escape(path_tail) + '-(?P<version>[0-9]*)')
            for tail in tails:
                match = pattern.match(tail)
                if match:
                    if len(match.group('version')) > 0:
                        version = int(match.group('version'))
                        if version > max_version:
                           max_version = version
            filename, extension = os.path.splitext(path_tail)
            
            newpath = os.path.join(subfolder, filename + '-' + str(max_version + 1) + extension)
        shutil.copy(path, os.path.join(self.project_path, newpath))
        return newpath
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
        newpath = self.copy_file('FASTA', path)
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
    def add_hla(self, hla_name):
        hla_rows = self.db_session.query(tPipeDB.HLA).filter_by(HLAName = hla_name).all()
        if len(hla_rows) > 0:
            raise HLAWithNameExistsError(hla_name)
        hla = tPipeDB.HLA(HLAName = hla_name)
        self.db_session.add(hla)
        self.db_session.commit()
        return hla.idHLA

        
        
        
    @staticmethod
    def createEmptyProject(project_path):
        if os.path.exists(project_path):
            raise ProjectPathAlreadyExistsError(project_path)
        else:
            os.mkdir(project_path)
            subfolders = ['FASTA', 'peptides', 'NetMHC', 'tide_indices', 'MGF', 'tide_search_results', 'percolator_results', 'misc', 'tide_param_files', 'assign_confidence_results', 'FilteredNetMHC', 'TargetSet']
            for subfolder in subfolders:
                os.mkdir(os.path.join(project_path, subfolder))
            return Project(project_path)


