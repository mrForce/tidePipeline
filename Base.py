import DB
from sqlalchemy import exists
import BashScripts
from create_target_set import *
import sys
import tempfile
from tabulate import tabulate
import configparser
import os
from Bio import SeqIO
from NetMHC import *
import glob
import re
import shutil
import configparser
import uuid
from fileFunctions import *
from datetime import datetime
import json
import TargetSetSourceCount
import ReportGeneration

from Errors import *
from Runners import *

    
    


class Base:
    def __init__(self, project_path, command, parent_base = False):        
        if parent_base:
            self.project_path = parent_base.project_path
            self.db_session = parent_base.db_session
            self.command = parent_base.command
            self.executables = parent_base.executables
        else:
            if os.path.isfile('reminder.txt'):
                subprocess.call(['cat', 'reminder.txt'])
                self.project_path = project_path
                print('project path: ' + project_path)
            
            self.db_session = DB.init_session(os.path.join(project_path, 'database.db'))
            self.command = DB.Command(commandString = command)
            self.db_session.add(self.command)
            self.db_session.commit()
            config = configparser.ConfigParser()
            config.read(os.path.join(project_path, 'config.ini'))
            self.executables = {}
            self.executables['netmhc'] = config['EXECUTABLES']['netmhc']
            self.executables['crux'] = config['EXECUTABLES']['crux']
            self.executables['msgfplus'] = config['EXECUTABLES']['msgfplus']
            self.executables['maxquant'] = config['EXECUTABLES']['maxquant']
            self.executables['msgf2pin'] = config['EXECUTABLES']['msgf2pin']


    def delete_row(self, row):
        if '__prepare_deletion__' in dir(row):
            row.__prepare_deletion__(self.project_path)
        self.db_session.delete(row)
        self.db_session.commit()
    def get_column_values(self, row_class, column_name):
        rows = self.db_session.query(row_class).all()
        values = []
        for x in rows:
            values.append(getattr(x, column_name))
        return values

    def verify_row_existence(self, column_object, name):
        """
        Basically, pass the ROW.Name object as column_object, and name as the name argument.

        For example, suppose we wanted to check if there was a TargetSet with the name "jordan", we would do:

        base_object.verify_row_existence(DB.TargetSet.TargetSetName, 'jordan')
        """
        return self.db_session.query(exists().where(column_object == name)).scalar()

    #search_type is either 'tide', 'msgfplus', 'msgf', or 'maxquant'
    def verify_search(self, search_type, search_name):
        searchbase_row = self.db_session.query(DB.SearchBase).filter_by(SearchName = search_name).first()
        if searchbase_row is None:
            return False
        else:
            if search_type == 'tide':
                return self.verify_row_existence(DB.TideSearch.idSearch, searchbase_row.idSearch)
            elif search_type in ['msgfplus', 'msgf']:
                return self.verify_row_existence(DB.MSGFPlusSearch.idSearch, searchbase_row.idSearch)
            elif search_type == 'maxquant':
                return self.verify_row_existence(DB.MaxQuantSearch.idSearch, searchbase_row.idSearch)
            else:
                raise InvalidSearchTypeError(search_type)

    def add_contaminant_file(self, path, contaminant_row_name, lengths, protein_format):
        print('format: ' + protein_format)
        print(protein_format == 'FASTA')
        directory = self.create_storage_directory('contaminants')
        filename = 'contaminants.fasta' if protein_format is 'FASTA' else 'contaminants.txt'
        shutil.copyfile(path, os.path.join(self.project_path, directory, filename))
        #the constructor for ContaminantSet extracts the peptides from the FASTA file and puts them in os.path.join(directory, 'contaminant_peptides.txt')
        if protein_format == 'FASTA':
            row = DB.ContaminantSet(self.project_path, os.path.join(directory, filename), os.path.join(directory, 'contaminant_set.txt'), lengths, contaminant_row_name, protein_format)
        elif protein_format == 'peptides':
            row = DB.ContaminantSet(self.project_path, os.path.join(directory, filename), None, lengths, contaminant_row_name, protein_format)
        else:
            assert(False)
        self.db_session.add(row)
        
    def add_param_file(self, program, name, path, comment = None):
        if '.' in path and (path.rfind('.') > path.rfind('/') if '/' in path else True):
            path_file_extension = path[(path.rfind('.') + 1)::]
        else:
            path_file_extension = False

        if program == 'percolator':
            if self.verify_row_existence(DB.PercolatorParameterFile.Name, name):
                raise ParameterFileNameMustBeUniqueError(name)
            new_path = os.path.join('tide_param_files', 'percolator_param_files', copy_file_unique_basename(path, os.path.join(self.project_path, 'tide_param_files', 'percolator_param_files'), path_file_extension))
            row = DB.PercolatorParameterFile(Name = name, Path = new_path, Comment = comment)
            self.db_session.add(row)
        elif program == 'assign-confidence':
            if self.verify_row_existence(DB.AssignConfidenceParameterFile.Name, name):
                raise ParameterFileNameMustBeUniqueError(name)
            new_path = os.path.join('tide_param_files', 'assign_confidence_param_files', copy_file_unique_basename(path, os.path.join(self.project_path, 'tide_param_files', 'assign_confidence_param_files'), path_file_extension))
            row = DB.AssignConfidenceParameterFile(Name = name, Path = new_path, Comment = comment)
            self.db_session.add(row)
        elif program == 'tide-search':
            if self.verify_row_existence(DB.TideSearchParameterFile.Name, name):
                raise ParameterFileNameMustBeUniqueError(name)
            new_path = os.path.join('tide_param_files', 'tide_search_param_files', copy_file_unique_basename(path, os.path.join(self.project_path, 'tide_param_files', 'tide_search_param_files'), path_file_extension))
            row = DB.TideSearchParameterFile(Name = name, Path = new_path, Comment = comment)
            self.db_session.add(row)
        elif program == 'tide-index':
            if self.verify_row_existence(DB.TideIndexParameterFile.Name, name):
                raise ParameterFileNameMustBeUniqueError(name)
            new_path = os.path.join('tide_param_files', 'tide_index_param_files', copy_file_unique_basename(path, os.path.join(self.project_path, 'tide_param_files', 'tide_index_param_files'), path_file_extension))
            row = DB.TideIndexParameterFile(Name = name, Path = new_path, Comment = comment)
            self.db_session.add(row)
        elif program == 'maxquant':
            if self.verify_row_existence(DB.MaxQuantParameterFile.Name, name):
                raise ParameterFileNameMustBeUniqueError(name)
            new_path = os.path.join('maxquant_param_files', copy_file_unique_basename(path, os.path.join(self.project_path, 'maxquant_param_files'), path_file_extension))
            row = DB.TideSearchParameterFile(Name = name, Path = new_path, Comment = comment)
            self.db_session.add(row)
        self.db_session.commit()



    def get_netmhc_executable_path(self):
        return self.executables['netmhc']
    def get_crux_executable_path(self):
        return self.executables['crux']
    def get_msgfplus_executable_path(self):
        return self.executables['msgfplus']
    def get_maxquant_executable_path(self):
        return self.executables['maxquant']
    def get_msgf2pin_executable_path(self):
        return self.executables['msgf2pin']


    def get_percolator_parameter_file(self, name):
        row = self.db_session.query(DB.PercolatorParameterFile).filter_by(Name = name).first()
        return row
    def get_assign_confidence_parameter_file(self, name):
        row = self.db_session.query(DB.AssignConfidenceParameterFile).filter_by(Name = name).first()
        return row
    def get_tide_search_parameter_file(self, name):
        row = self.db_session.query(DB.TideSearchParameterFile).filter_by(Name = name).first()
        return row
    def get_tide_index_parameter_file(self, name):
        row = self.db_session.query(DB.TideIndexParameterFile).filter_by(Name = name).first()
        return row
    def get_tide_index(self, name):
        row = self.db_session.query(DB.TideIndex).filter_by(TideIndexName = name).first()
        return row
    #returns row or None
    def get_maxquant_parameter_file(self, name):
        row = self.db_session.query(DB.MaxQuantParameterFile).filter_by(Name = name).first()
        return row
    def add_maxquant_parameter_file(self, path, name, comment = None):
        internal_filename = str(uuid.uuid4()) + '.xml'
        while os.path.exists(os.path.join(self.project_path, 'maxquant_param_files', internal_filename)):
            internal_filename = str(uuid.uuid4()) + '.xml'
        shutil.copyfile(path, os.path.join(os.path.join(self.project_path, 'maxquant_param_files', internal_filename)))
        maxquant_param_row = None
        if comment is not None and len(comment) > 0:
            maxquant_param_row = DB.MaxQuantParameterFile(Name = name, Path = os.path.join('maxquant_param_files', internal_filename), Comment = comment)
        else:
            maxquant_param_row = DB.MaxQuantParameterFile(Name = name, Path = os.path.join('maxquant_param_files', internal_filename))
        self.db_session.add(maxquant_param_row)
        self.db_session.commit()
    def list_maxquant_parameter_files(self):
        headers = ['id', 'Name', 'Path', 'Comment']
        rows = []
        for row in self.db_session.query(DB.MaxQuantParameterFile).all():
            rows.append([str(row.idMaxQuantParameterFile), row.Name, row.Path, '' if row.Comment is None else row.Comment])
        return tabulate(rows, headers=headers)
    def get_maxquant_search_row(self, name):
        return self.db_session.query(DB.MaxQuantSearch).filter_by(SearchName = name).first()
    def create_storage_directory(self, parent_path):
        """
        This function is for creating a "storage directory", which is a randomly named (using uuid.uuid4) directory within parent_path. parent_path is relative to the project. 

        For example, if I wanted to create a new msgfplus index, I wolud first call create_storage_director('msgfplus_indices')
        """
        full_path = os.path.join(self.project_path, parent_path)
        print('full path: ' + full_path)
        assert(os.path.isdir(full_path))
        dir_name = str(uuid.uuid4())
        while os.path.exists(os.path.join(full_path, dir_name)):
            dir_name = str(uuid.uuid4())
        long_path = os.path.join(full_path, dir_name)
        os.makedirs(long_path)
        return os.path.join(parent_path, dir_name)
        
    def get_list_filtered_netmhc(self, peptide_list_name = None, hla=None):
        #joined = self.db_session.query(DB.FilteredNetMHC, DB.NetMHC).join(DB.NetMHC).join(DB.FilteredNetMHC.netmhc).join(DB.NetMHC.hla).join(DB.NetMHC.peptidelist)
        joined = self.db_session.query(DB.FilteredNetMHC, DB.NetMHC, DB.PeptideList, DB.HLA).join(DB.NetMHC).join(DB.PeptideList).join(DB.HLA)
        if peptide_list_name:
            joined = joined.filter(DB.PeptideList.peptideListName == peptide_list_name)
        if hla:
            joined = joined.filter(DB.HLA.HLAName == hla)
        joined_rows = joined.all()
        results = []
        header = ['ID', 'Filtered NetMHC Name', 'path', 'HLA', 'rank cutoff', 'PeptideList Name']
        for row in joined_rows:
            print('row: ')
            print(str(row))
            results.append({'ID': str(row.FilteredNetMHC.idFilteredNetMHC), 'Filtered NetMHC Name': row.FilteredNetMHC.FilteredNetMHCName, 'path': row.FilteredNetMHC.filtered_path, 'HLA': row.HLA.HLAName, 'rank cutoff': str(row.FilteredNetMHC.RankCutoff), 'PeptideList Name' : row.PeptideList.peptideListName})
        return (header, results)
    def get_filtered_netmhc_row(self, name):
        return self.db_session.query(DB.FilteredNetMHC).filter_by(FilteredNetMHCName = name).first()
    def get_netmhc_row(self, name):
        return self.db_session.query(DB.NetMHC).filter_by(Name=name).first()
    def get_target_set_row(self, name):
        return self.db_session.query(DB.TargetSet).filter_by(TargetSetName = name).first()
    def get_peptide_list_row(self, name):
        return self.db_session.query(DB.PeptideList).filter_by(peptideListName = name).first()

    def list_targetsets(self):
        rows = self.db_session.query(DB.TargetSet).all()
        headers = ['ID', 'Name', 'Sources']
        results = []
        for row in rows:
            row_id = str(row.idTargetSet)
            name = str(row.TargetSetName)
            source_id_map = json.loads(str(row.SourceIDMap))
            results.append([row_id, name, 'Filtered NetMHC: ' + ', '.join(source_id_map['filtered_netmhc'].values()) + '\n' + 'Peptide Lists: ' + ', '.join(source_id_map['peptide_lists'].values())])
        return tabulate(results, headers=headers)

    
    def add_targetset(self, netmhc_filter_names, peptide_list_names, target_set_name):
        #need to create lists of the form [(name, location)...]
        netmhc_filter_locations = []
        peptide_list_locations = []
        if netmhc_filter_names:
            for name in netmhc_filter_names:
                row  = self.db_session.query(DB.FilteredNetMHC).filter_by(FilteredNetMHCName = name).first()
                if row:
                    location = os.path.join(self.project_path, row.filtered_path)
                    netmhc_filter_locations.append((name, location))
                else:
                    raise NoSuchFilteredNetMHCError(name)
        if peptide_list_names:
            for name in peptide_list_names:
                row = self.db_session.query(DB.PeptideList).filter_by(peptideListName = name).first()
                if row:
                    location = os.path.join(self.project_path, row.PeptideListPath)
                    peptide_list_locations.append((name, location))
                else:
                    raise NoSuchPeptideListError(name)
        if self.db_session.query(DB.TargetSet).filter_by(TargetSetName = target_set_name).first():
            raise TargetSetNameMustBeUniqueError(target_set_name)
        
        output_folder = str(uuid.uuid4())
        while os.path.isdir(os.path.join(self.project_path, 'TargetSet', output_folder)) or os.path.isfile(os.path.join(self.project_path, 'TargetSet', output_folder)):
            output_folder = str(uuid.uuid4())
        os.mkdir(os.path.join(self.project_path, 'TargetSet', output_folder))
        output_fasta_location = os.path.join(self.project_path, 'TargetSet', output_folder, 'targets.fasta')
        output_json_location = os.path.join(self.project_path, 'TargetSet', output_folder, 'sources.json')

        source_id_map = create_target_set(netmhc_filter_locations, peptide_list_locations, output_fasta_location, output_json_location)
        target_set_row = DB.TargetSet(TargetSetFASTAPath = os.path.join('TargetSet', output_folder, 'targets.fasta'), PeptideSourceMapPath=os.path.join('TargetSet', output_folder, 'sources.json'), SourceIDMap=json.dumps(source_id_map), TargetSetName = target_set_name)
        self.db_session.add(target_set_row)
        self.db_session.commit()
    def verify_filtered_netMHC(self, name):
        if self.db_session.query(DB.FilteredNetMHC).filter_by(FilteredNetMHCName = name).first():
            return True
        else:
            return False
    def verify_target_set(self, name):
        if self.db_session.query(DB.TargetSet).filter_by(TargetSetName = name).first():
            return True
        else:
            return False

    def add_mgf_file(self, path, name, partOfIterativeSearch = False):
        row = self.db_session.query(DB.MGFfile).filter_by(MGFName = name).first()
        if row:
            raise MGFNameMustBeUniqueError(name)
        else:
            newpath = self.copy_file('MGF', path)
            mgf_record = DB.MGFfile(MGFName = name, MGFPath = newpath, partOfIterativeSearch = partOfIterativeSearch)
            self.db_session.add(mgf_record)
            self.db_session.commit()
            return mgf_record
    def add_raw_file(self, path, name):
        row = self.db_session.query(DB.RAWfile).filter_by(RAWName = name).first()
        if row:
            raise RAWNameMustBeUniqueError(name)
        else:
            newpath = self.copy_file('RAW', path)
            raw_record = DB.RAWfile(RAWName = name, RAWPath = newpath)
            self.db_session.add(raw_record)
            self.db_session.commit()
            return raw_record
    def verify_peptide_list(self, peptide_list_name):
        row = self.db_session.query(DB.PeptideList).filter_by(peptideListName = peptide_list_name).first()
        if row is None:
            return False
        else:
            return True

    def verify_hla(self, hla):
        row = self.db_session.query(DB.HLA).filter_by(HLAName = hla).first()
        if row is None:
            return False
        else:
            return True

    def run_netmhc(self, peptide_list_name, hla, rank_cutoff, netmhc_name, filtered_name, netmhcpan = False):
        netmhc_row, pep_score_path, is_netmhc_row_new = self._run_netmhc(peptide_list_name, hla, netmhc_name, netmhcpan)
       
        if is_netmhc_row_new:
            filtered_netmhc_row = None
        else:
            filtered_netmhc_row = self.db_session.query(DB.FilteredNetMHC).filter_by(idNetMHC = netmhc_row.idNetMHC, RankCutoff = rank_cutoff).first()

        if filtered_netmhc_row is None:
            file_name = str(uuid.uuid4())
            while os.path.isfile(os.path.join(self.project_path, 'FilteredNetMHC', file_name)) or os.path.isdir(os.path.join(self.project_path, 'FilteredNetMHC', file_name)):
                file_name = str(uuid.uuid4())
            print('current place: ' + os.getcwd())
            output_path = os.path.join(self.project_path, 'FilteredNetMHC', file_name)
            input_path = os.path.join(self.project_path, pep_score_path)
            rank_cutoff_float = float(rank_cutoff)
            with open(input_path, 'r') as f:
                with open(output_path, 'w') as g:
                    for line in f:
                        parts = line.split(',')
                        if len(parts) == 2:
                            peptide = parts[0].strip()
                            rank = float(parts[1])
                            if rank <= rank_cutoff_float:
                                g.write(peptide + '\n')
            
                                
            filtered_row = DB.FilteredNetMHC(netmhc=netmhc_row, RankCutoff = rank_cutoff, FilteredNetMHCName = filtered_name, filtered_path = os.path.join('FilteredNetMHC', file_name))
            self.db_session.add(filtered_row)
            #self.db_session.commit()
            
                
    def import_netmhc_run(self, hla, location, peptidelist_name, ranks=None):
        #location is the NetMHC output
        peptide_list_row = self.db_session.query(DB.PeptideList).filter_by(peptideListName = peptidelist_name).first()
        if peptide_list_row is None:
            raise NoSuchPeptideListError(peptidelist_name)
        hla_row = self.db_session.query(DB.HLA).filter_by(HLAName=hla).first()
        if hla_row is None:
            raise NoSuchHLAError(hla)
        netmhc_row = self.db_session.query(DB.NetMHC).filter_by(peptidelistID=peptide_list_row.idPeptideList, idHLA=hla_row.idHLA).first()
        if netmhc_row:
            raise DuplicateNetMHCError(peptidelist_name, hla)
        else:
            netmhc_output_filename = str(uuid.uuid4().hex)
            while os.path.isfile(os.path.join(self.project_path, 'NetMHC', netmhc_output_filename)) or os.path.isfile(os.path.join(self.project_path, 'NetMHC', netmhc_output_filename + '-parsed')):
                netmhc_output_filename = str(uuid.uuid4().hex)
            shutil.copy(location, os.path.join(self.project_path, 'NetMHC', netmhc_output_filename))
            affinity_path = os.path.join('NetMHC', netmhc_output_filename + '-affinity')
            rank_path =  os.path.join('NetMHC', netmhc_output_filename + '-rank')
            full_output_path = os.path.join(self.project_path, 'NetMHC', netmhc_output_filename)
            BashScripts.extract_netmhc_output(full_output_path, os.path.join(self.project_path, affinity_path))
            BashScripts.netmhc_percentile(os.path.abspath(os.path.join(self.project_path, affinity_path)), os.path.abspath(os.path.join(self.project_path, rank_path)))

            netmhc_row = DB.NetMHC(peptidelist = peptide_list_row, hla = hla_row, Name = peptidelist_name + '_' + hla, NetMHCOutputPath= os.path.join('NetMHC', netmhc_output_filename), PeptideAffinityPath = affinity_path, PeptideRankPath=rank_path)
            self.db_session.add(netmhc_row)
            self.db_session.commit()
            if ranks:
                for rank_cutoff in ranks:
                    filtered_name = peptidelist_name + '_' + hla + '_' + rank_cutoff
                    file_name = str(uuid.uuid4())
                    while os.path.isfile(os.path.join(self.project_path, 'FilteredNetMHC', file_name)) or os.path.isdir(os.path.join(self.project_path, 'FilteredNetMHC', file_name)):
                        file_name = str(uuid.uuid4())
                    output_path = os.path.join(self.project_path, 'FilteredNetMHC', file_name)
                    input_path = os.path.join(self.project_path, rank_path)
                    rank_cutoff_float = float(rank_cutoff)
                    with open(input_path, 'r') as f:
                        with open(output_path, 'w') as g:
                            for line in f:
                                parts = line.split(',')
                                if len(parts) == 2:
                                    peptide = parts[0].strip()
                                    rank = float(parts[1])
                                    if rank <= rank_cutoff_float:
                                        g.write(peptide + '\n')
                    filtered_row = DB.FilteredNetMHC(netmhc=netmhc_row, RankCutoff = rank_cutoff, FilteredNetMHCName = filtered_name, filtered_path = os.path.join('FilteredNetMHC', file_name))
                    self.db_session.add(filtered_row)

            
    def import_peptide_list(self, name, fasta_name, location):
        fasta_row = self.db_session.query(DB.FASTA).filter_by(Name=fasta_name).first()
        if fasta_row is None:
            raise FASTAWithNameDoesNotExistError(fasta_name)
        line_length_set = list(filter(lambda x: x > 0, BashScripts.line_length_set(location)))
        assert(len(line_length_set) == 1)
        length = list(line_length_set)[0]
        peptide_row = self.db_session.query(DB.PeptideList).filter_by(length = length, fasta = fasta_row).first()
        if peptide_row is None:
            fasta_filename = os.path.split(fasta_row.FASTAPath)[1]
            peptide_filename = fasta_filename + '_' + str(length) + '.txt'
            peptide_list_path = os.path.join('peptides', peptide_filename)
            shutil.copyfile(location, os.path.join(self.project_path, peptide_list_path))
            peptide_list = DB.PeptideList(peptideListName = name, length = length, fasta = fasta_row, PeptideListPath = peptide_list_path)
            self.db_session.add(peptide_list)
            self.db_session.commit()
    def add_peptide_list(self, name, length, fasta_name):
        fasta_row = self.db_session.query(DB.FASTA).filter_by(Name=fasta_name).first()
        if fasta_row is None:
            raise FASTAWithNameDoesNotExistError(fasta_name)
        print('length:')
        print(length)
        peptide_row = self.db_session.query(DB.PeptideList).filter_by(length = length, fasta = fasta_row).first()
        if peptide_row is None:
            fasta_filename = os.path.split(fasta_row.FASTAPath)[1]
            peptide_filename = fasta_filename + '_' + str(length) + '.txt'
            peptide_list_path = os.path.join('peptides', peptide_filename)
            if not os.path.isfile(os.path.join(self.project_path, peptide_list_path)):
                peptides = extract_peptides(os.path.join(self.project_path, fasta_row.FASTAPath), length)
                write_peptides(os.path.join(self.project_path, peptide_list_path), peptides)
            peptide_list = DB.PeptideList(peptideListName = name, length = length, fasta = fasta_row, PeptideListPath = peptide_list_path)
            self.db_session.add(peptide_list)
            self.db_session.commit()

    
                    
            
            
            
    def _run_netmhc(self, peptide_list_name, hla_name, netmhc_name, netmhcpan = False):
        """
        This first checks if there's already a in NetMHC for the given peptide list and HLA. If there is, then it just returns a tuple of the form: (netmhc_row, PeptideRankPath)
        
        If there isn't, then it runs NetMHC, inserts a row into the table, and returns (netmhc_row, PeptideRankPath)               
        """
        peptide_list_row = self.db_session.query(DB.PeptideList).filter_by(peptideListName=peptide_list_name).first()
        if peptide_list_row is None:
            raise NoSuchPeptideListError(peptide_list_name)
        hla_row = self.db_session.query(DB.HLA).filter_by(HLAName=hla_name).first()
        if hla_row is None:
            raise NoSuchHLAError(hla_name)
        netmhc_row = self.db_session.query(DB.NetMHC).filter_by(peptidelistID=peptide_list_row.idPeptideList, idHLA=hla_row.idHLA, Name=netmhc_name).first()
        if netmhc_row:
            return (netmhc_row, netmhc_row.PeptideRankPath, False)
        else:
            netmhc_output_filename = str(uuid.uuid4().hex)
            while os.path.isfile(os.path.join(self.project_path, 'NetMHC', netmhc_output_filename)) or os.path.isfile(os.path.join(self.project_path, 'NetMHC', netmhc_output_filename + '-parsed')):
                netmhc_output_filename = str(uuid.uuid4().hex)
            call_netmhc(self.executables['netmhc'], hla_name, os.path.join(self.project_path, peptide_list_row.PeptideListPath), os.path.join(self.project_path, 'NetMHC', netmhc_output_filename))
            affinity_path = os.path.join('NetMHC', netmhc_output_filename + '-affinity')
            rank_path =  os.path.join('NetMHC', netmhc_output_filename + '-rank')
            full_output_path = os.path.join(self.project_path, 'NetMHC', netmhc_output_filename)
            BashScripts.extract_netmhc_output(full_output_path, os.path.join(self.project_path, affinity_path))
            BashScripts.netmhc_percentile(os.path.abspath(os.path.join(self.project_path, affinity_path)), os.path.abspath(os.path.join(self.project_path, rank_path)))
            
            netmhc_row = DB.NetMHC(peptidelistID=peptide_list_row.idPeptideList, idHLA = hla_row.idHLA, Name = netmhc_name, NetMHCOutputPath=os.path.join('NetMHC', netmhc_output_filename), PeptideRankPath = rank_path, PeptideAffinityPath=affinity_path)
            self.db_session.add(netmhc_row)
            self.db_session.commit()
            return (netmhc_row, netmhc_row.PeptideRankPath, True)


    def list_peptide_lists(self):
        peptide_lists = []
        peptide_list_rows = self.db_session.query(DB.PeptideList).all()
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
        rows = self.db_session.query(DB.FASTA).all()
        fastas = []
        for row in rows:
            fasta = {'id': row.idFASTA, 'name': row.Name, 'comment': row.Comment, 'path': row.FASTAPath, 'peptide_lists': []}
            for pList in row.peptide_lists:
                fasta['peptide_lists'].append({'name': pList.peptideListName, 'length': pList.length})
            fastas.append(fasta)
        return fastas
    def list_mgf_db(self):
        rows = self.db_session.query(DB.MGFfile).all()        
        mgfs = []
        for row in rows:
            mgf = {'id': row.idMGFfile, 'name': row.MGFName, 'path': row.MGFPath, 'partOfIterativeSearch': row.partOfIterativeSearch}
            mgfs.append(mgf)
        return mgfs


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
        fasta_rows = self.db_session.query(DB.FASTA).all()
        for row in fasta_rows:
            path = row.FASTAPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                print('FASTA path: ' + row.FASTAPath)
                raise FASTAMissingError(row.idFASTA, row.Name, row.FASTAPath)
        print('going to check peptide list rows')
        peptide_list_rows = self.db_session.query(DB.PeptideList).all()
        for row in peptide_list_rows:
            path = row.PeptideListPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                raise PeptideListFileMissingError(row.idPeptideList, row.peptideListName, row.PeptideListPath)
        print('going to check mgf rows')
        mgf_rows = self.db_session.query(DB.MGFfile).all()
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
        if len(self.db_session.query(DB.FASTA).filter_by(Name=name).all()) > 0:
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
        fasta_record = DB.FASTA(Name = name, FASTAPath = newpath, Comment = comment)
        self.db_session.add(fasta_record)
        #self.db_session.commit()
        return fasta_record
    def get_commands(self):
        commands = []
        for row in self.db_session.query(DB.Command):
            commands.append(row)
        return commands


    def list_hla(self):
        query = self.db_session.query(DB.HLA)
        rows = query.all()
        hlas = []
        for row in rows:
            hla = {'name': row.HLAName, 'id': str(row.idHLA)}
            hlas.append(hla)
        return hlas
    def add_hla(self, hla_name):
        hla_rows = self.db_session.query(DB.HLA).filter_by(HLAName = hla_name).all()
        if len(hla_rows) > 0:
            raise HLAWithNameExistsError(hla_name)
        hla = DB.HLA(HLAName = hla_name)
        self.db_session.add(hla)
        #self.db_session.commit()
        return hla

        
        
        
    @staticmethod
    def createEmptyProject(project_path, command, config_location, unimod_xml_location):
        if os.path.exists(project_path):
            raise ProjectPathAlreadyExistsError(project_path)
        else:
            print('going to get config')
            config = configparser.ConfigParser()
            print('config location: ' + config_location)
            config.read(config_location)
            print('config reading')
            print(config)
            assert('EXECUTABLES' in config.sections())
            config_keys = ['netmhc', 'crux', 'msgfplus', 'msgf2pin']
            for key in config_keys:
                print('key: ' + key)
                assert(key in config['EXECUTABLES'])
                value = config['EXECUTABLES'][key]
                assert(len(value) > 0)
            os.mkdir(project_path)
            subfolders = ['FASTA', 'contaminants', 'peptides', 'NetMHC', 'tide_indices', 'MGF', 'tide_search_results', 'percolator_results', 'misc', 'tide_param_files', 'assign_confidence_results', 'FilteredNetMHC', 'TargetSet', 'msgfplus_indices', 'msgfplus_search_results', 'FilteredSearchResult', 'maxquant_param_files', 'RAW', 'maxquant_search', 'tide_param_files/assign_confidence_param_files', 'tide_param_files/percolator_param_files', 'tide_param_files/tide_search_param_files', 'tide_param_files/tide_index_param_files']
            for subfolder in subfolders:
                os.makedirs(os.path.join(project_path, subfolder))
            shutil.copy(config_location, os.path.join(project_path, 'config.ini'))
            shutil.copy(unimod_xml_location, os.path.join(project_path, 'unimod.xml'))
            return Base(project_path, command)



