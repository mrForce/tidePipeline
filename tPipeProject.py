import tPipeDB
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
CRUX_BINARY = '/home/jforce/crux_install/bin/crux'
class Error(Exception):
    pass

class AssignConfidenceFailedError(Error):
    def __init__(self, command):
        self.message = 'assign-confidence command: ' + command + ' failed'
    def __repr__(self):
        return self.message
    
class MGFFileMissingError(Error):
    def __init__(self, idMGFfile, name, path):
        self.message = 'MGF file with ID: ' + str(idMGFfile) + ' and name: ' + name + ' and path: ' + path + ' is missing'
    def __repr__(self):
        return self.message
    
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
class NoSuchPeptideListError(Error):
    def __init__(self, peptide_list_name):
        self.message = 'There is no row in the PeptideList table with the name: ' + peptide_list_name

    def __repr__(self):
        return self.message

class NoSuchHLAError(Error):
    def __init__(self, hla_name):
        self.message = 'There is no HLA with the name: ' + hla_Name
    def __repr__(self):
        return self.message

class PeptideListFileMissingError(Error):
    def __init__(self, peptide_list_id, peptide_list_name, path):
        self.message = 'The row in the PeptideList table, with id: ' + str(peptide_list_id) + ' and name: ' + str(peptide_list_name) + ' points to a peptide file with path: ' + path + ', but this file does not exist.'
    def __repr__(self):
        return self.message

class MGFRowDoesNotExistError(Error):
    def __init__(self, name):
        self.message = 'There is no MGF file with the name: ' + name

    def __repr__(self):
        return self.message
class MGFNameMustBeUniqueError(Error):
    def __init__(self, name):
        self.message = 'There\'s already an MGF file with the name: ' + name

    def __repr__(self):
        return self.message
    
class TideIndexFailedError(Error):
    def __init__(self, command):
        self.message = 'The tide-search command ended: ' + command + ' with non-zero exit code'
    def __repr__(self):
        return self.message


class NoSuchTideIndexError(Error):
    def __init__(self, name):
        self.message = 'There is no tide index with the name: ' + name
    def __repr__(self):
        return self.message
class TideSearchFailedError(Error):
    def __init__(self, command):
        self.message = 'The tide-search command ended: ' + command + ' with non-zero exit code'
    def __repr__(self):
        return self.message

class TideSearchNameMustBeUniqueError(Error):
    def __init__(self, name):
        self.message = 'There is already a Tide Search with the name: ' + name
    def __repr__(self):
        return self.message

class TideSearchRunner:
    def __init__(self, tide_search_options):
        self.tide_search_options = tide_search_options
    @staticmethod
    def get_tide_search_options():
        return {'--mod-precision': {'type':int}, '--auto-precursor-window': {'choices': ['false', 'warn', 'fail']}, '--max-precursor-charge': {'type': int}, '--precursor-window': {'type': float}, '--precursor-window-type': {'choices': ['mass', 'mz', 'ppm']}, '--auto-mz-bin-width': {'choices': ['false', 'warn', 'fail']}, '--compute-sp': {'choices': ['T', 'F']}, '--deisotope': {'type': float}, '--exact-p-value': {'choices':['T', 'F']}, '--isotope-error': {'type': str}, '--min-peaks': {'type': int}, '--mz-bin-offset': {'type': float}, '--mz-bin-width': {'type': float}, '--peptide-centric-search': {'choices': ['T', 'F']}, '--score-function': {'choices': ['xcorr', 'residue-evidence', 'both']}, '--fragment-tolerance': {'type': float}, '--evidence-granularity': {'type': int}, '--remove-precursor-peak': {'choices': ['T', 'F']}, '--remove-precursor-tolerance': {'type': float}, '--scan-number': {'type': str}, '--skip-processing': {'choices': ['T', 'F']}, '--spectrum-charge': {'choices': ['1', '2', '3', 'all']}, '--spectrum-max-mz': {'type': float}, '--spectrum-min-mz': {'type': float}, '--use-flanking-peaks': {'choices': ['T', 'F']}, '--use-neutral-loss-peaks': {'choices': ['T', 'F']}, '--num-threads': {'type': int}, '--pm-charge': {'type': int}, '--pm-max-frag-mz': {'type': float}, '--pm-max-precursor-delta-ppm': {'type': float}, '--pm-max-precursor-mz': {'type': float}, '--pm-max-scan-seperation': {'type': int}, '--pm-min-common-frag-peaks': {'type': int}, '--pm-min-frag-mz': {'type': float}, '--pm-min-peak-pairs': {'type': int}, '--pm-min-precursor-mz': {'type': float}, '--pm-min-scan-frag-peaks': {'type': int}, '--pm-pair-top-n-frag-peaks': {'type': int}, '--pm-top-n-frag-peaks': {'type': int}, '--concat': {'choices': ['T', 'F']}, '--file-column': {'choices': ['T', 'F']}, '--fileroot': {'type': str}, '--mass-precision': {'type': int}, '--mzid-output': {'choices': ['T', 'F']}, '--precision': {'type': int}, '--spectrum-parser': {'choices': ['pwiz', 'mstoolkit']}, '--store-spectra': {'type': str}, '--top-match': {'type': int}, '--use-z-line': {'choices': ['T', 'F']}}

    #change the options here
    def run_search_create_row(self, mgf_row, index_row, output_directory_tide, output_directory_db, options, project_path, tide_search_row_name):        
        """ First, decide the filename """
        param_filename = str(uuid.uuid4().hex) + '-param.txt'
        while os.path.isfile(os.path.join(project_path, 'tide_param_files', param_filename)):
            param_filename = str(uuid.uuid4().hex) + '-param.txt'
        with open(os.path.join(project_path, 'tide_param_files', param_filename)) as f:        
            for k, v in options.values():
                f.write(k + '=' + str(v) + '\n')
        spectra_file = os.path.join(project_path, 'MGF', mgf_row.MGFPath)
        index_filename = os.path.join(project_path, 'tide_indices', index_row.TideIndexPath)
        command = [CRUX_BINARY, 'tide-search', '--output-dir', output_directory_tide, '--parameter-file', os.path.join(project_path, 'tide_param_files', param_filename), spectra_file, index_filename]
        try:
            p = subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise TideSearchFailedError(' '.join(command))
        search_row = tPipeDB.TideSearch(idTideIndex = index_row.idTideIndex, idMGF=mgf_row.idMGFfile, targetPath=os.path.join(output_directory_db, 'tide-search.target.txt'), decoyPath=os.path.join(output_directory_db, 'tide-search.decoy.txt'), paramsPath=os.path.join('tide_param_files', param_filename), logPath=os.path.join(output_directory_db, 'tide-search.log.txt'), TideSearchName=tide_search_row_name)
        return search_row

        
class TideIndexRunner:
    def __init__(self, tide_index_options):
        #tide_index_options is a dictionary.
        self.tide_index_options = tide_index_options


    @staticmethod
    def get_tide_index_options():
        return {'--clip-nterm-methionine': {'choices':['T', 'F']}, '--isotopic-mass': {'choices': ['average', 'mono']}, '--max-length': {'type': int}, '--max-mass': {'type':str}, '--min-length': {'type':int}, '--min-mass': {'type':str}, '--cterm-peptide-mods-spec': {'type': str}, '--max-mods': {'type': int}, '--min-mods': {'type':int}, '--mod-precision': {'type':int}, '--mods-spec': {'type': str}, '--nterm-peptide-mods-spec': {'type':str}, '--allow-dups': {'choices': ['T', 'F']}, '--decoy-format': {'choices': ['none', 'shuffle', 'peptide-reverse', 'protein-reverse']}, '--decoy-generator': {'type':str}, '--keep-terminal-aminos': {'choices': ['N', 'C', 'NC', 'none']}, '--seed': {'type':str}, '--custom-enzyme': {'type': str}, '--digestion': {'choices': ['full-digest', 'partial-digest', 'non-specific-digest']}, '--enzyme': {'choices': ['no-enzyme', 'trypsin', 'trypsin/p', 'chymotrypsin', 'elactase', 'clostripain', 'cyanogen-bromide', 'iodosobenzoat', 'proline-endopeptidase', 'staph-protease', 'asp-n', 'lys-c', 'lys-n', 'arg-c', 'glu-c', 'pepsin-a', 'elastase-trypsin-chymotrypsin', 'custom-enzyme']}, '--missed-cleavages': {'type': int}}
    @staticmethod
    def convert_cmdline_option_to_column_name(option):
        converter = {'clip-nterm-methionine': 'clip_nterm_methionine', 'isotopic-mass': 'isotopic_mass', 'max-length': 'max_length', 'max-mass': 'max_mass', 'min-length': 'min_length', 'min-mass': 'min_mass', 'cterm-peptide-mods-spec': 'cterm_peptide_mods_spec', 'max-mods': 'max_mods', 'min-mods':'min_mods', 'mod-precision': 'mod_precision', 'mods-spec': 'mods_spec', 'nterm-peptide-mods-spec': 'nterm_peptide_mods_spec', 'allow-dups': 'allow_dups', 'decoy-format': 'decoy_format', 'decoy-generator': 'decoy_generator', 'keep-terminal-aminos': 'keep_terminal_aminos', 'seed': 'seed', 'custom-enzyme': 'custom_enzyme', 'digestion': 'digestion', 'enzyme': 'enzyme', 'missed-cleavages': 'missed_cleavages'}
        if option in converter:
            return converter[option]
        else:
            return None
    def run_index_create_row(self, fasta_path, output_directory_tide, output_directory_db, index_filename):
        #first, need to create the tide-index command
        command = [CRUX_BINARY, 'tide-index']
        for k,v in self.tide_index_options.items():
            if k and v:
                command.append('--' + k)
                command.append(v)
        command.append('--output-dir')
        command.append(output_directory_tide)
        command.append(fasta_path)
        command.append(os.path.join(output_directory_tide, index_filename))
        print('command')
        print(' '.join(command))
        try:
            p = subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise TideIndexFailedError(' '.join(command))
        column_arguments = {}
        for k, v in self.tide_index_options.items():
            column_name = TideIndexRunner.convert_cmdline_option_to_column_name(k)
            if column_name:
                column_arguments[column_name] = v
        column_arguments['TideIndexPath'] = os.path.join(output_directory_db, index_filename)
        return tPipeDB.TideIndex(**column_arguments)

class AssignConfidenceRunner:
    def __init__(self, assign_confidence_options):
        self.assign_confidence_options = assign_confidence_options
        


    @staticmethod
    def get_assign_confidence_options():
        return {'--estimation-method': {'choices': ['min-max', 'tdc', 'peptide-level']}, '--score': {'type': str}, '--sidak': {'choices': ['T', 'F']}, '--top-match-in': {'type': int}, '--combine-charge-states': {'choices': ['T', 'F']}, '--combine-modified-peptides': {'choices': ['T', 'F']}}

    @staticmethod
    def convert_cmdline_option_to_column_name(option):
        converter = {'estimation-method': 'estimation_method', 'score': 'score', 'sidak': sidak, 'top-match-in': 'top_match_in', 'combine-charge-states': 'combine_charge_states', 'combine-modified-peptides': 'combine_modified_peptides'}
        if option in converter:
            return converter[option]
        else:
            return None

    def run_assign_confidence_create_row(self, target_path, output_directory_tide, output_directory_db):
        #first, need to create the tide-index command
        command = [CRUX_BINARY, 'assign-confidence']
        for k,v in self.assign_confidence_options.items():
            if k and v:
                command.append('--' + k)
                command.append(v)
        command.append('--output-dir')
        command.append(output_directory_tide)
        command.append(target_path)

        print('command')
        print(' '.join(command))
        try:
            p = subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise AssignConfidenceFailedError(' '.join(command))
        column_arguments = {}
        for k, v in self.assign_confidence_options.items():
            column_name = AssignConfidenceRunner.convert_cmdline_option_to_column_name(k)
            if column_name:
                column_arguments[column_name] = v
        column_arguments['AssignConfidenceOutputPath'] = output_directory_db
        return tPipeDB.AssignConfidence(**column_arguments)


class Project:
    def __init__(self, project_path, command):
        self.project_path = project_path
        print('project path: ' + project_path)
        self.db_session = tPipeDB.init_session(os.path.join(project_path, 'database.db'))
        self.command = tPipeDB.Command(commandString = command)
        self.db_session.add(self.command)
        self.db_session.commit()

    def assign_confidence(self, tide_search_name, options):
        tide_search_row = self.db_session.query(tPipeDB.AssignConfidence).filter_by(TideSearchName = tide_search_name).first()

            
    def run_tide_search(self, mgf_name, tide_index_name, tide_search_runner, tide_search_name, options):
        mgf_row = self.db_session.query(tPipeDB.MGFFile).filter_by(MGFName = mgf_name).first()
        tide_index_row = self.db_session.query(tPipeDB.TideIndex).filter_by(TideIndexName=tide_index_name).first()
        tide_search_row = self.db_session.query(tPipeDB.TideSearch).filter_by(TideSearchName=tide_search_name).first()
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
    def add_mgf_file(self, path, name):
        row = self.db_session.query(tPipeDB.MGFfile).filter_by(MGFName = name).first()
        if row:
            raise MGFNameMustBeUniqueError(name)
        else:
            newpath = self.copy_file('MGF', path)
            mgf_record = tPipeDB.MGFfile(MGFName = name, MGFPath = newpath)
            self.db_session.add(mgf_record)
            self.db_session.commit()
            return fasta_record.idMGFfile    
    def get_tide_indices(self):
        rows = self.db_session.query(tPipeDB.TideIndex).all()
        indices = []
        for row in rows:
            index = {'name': row.TideIndexName, 'id': str(row.idTideIndex), 'path':row.TideIndexPath, 'peptide_lists':[], 'filteredNetMHCs':[]}
            for l in row.peptidelists:
                index['peptide_lists'].append({'name': l.peptideListName, 'length': str(l.length), 'fasta_name': l.fasta.Name})
            for n in row.filteredNetMHCs:
                netmhc = self.db_session.query(tPipeDB.NetMHC).filter_by(idNetMHC=n.idNetMHC).first()
                if netmhc:
                    peptide_list_row = self.db_session.query(tPipeDB.PeptideList).filter_by(idPeptideList=netmhc.peptidelistID).first()
                    hla_row = self.db_session.query(tPipeDB.HLA).filter_by(idHLA=netmhc.idHLA).first()
                    if peptide_list_row and hla_row:
                        index['filteredNetMHCs'].append({'hla': hla_row.HLAName, 'name': peptide_list_row.peptideListName, 'length': str(peptide_list_row.length), 'fasta_name': peptide_list_row.fasta.Name})
            indices.append(index)
        return indices

    def create_tide_index(self, peptide_list_names, netmhc_filters, tide_index_runner, tide_index_name):
        """
        peptide_list_names is a list of strings, where each is the name of a PeptideList

        Each netmhc filter is a tuple of the form (HLA_name, peptide list name, rank cutoff)
        
        tide_index_runner is an instance of the TideIndexRunner class
        """
        temp_files = []
        filtered_netmhc_rows = []
        if netmhc_filters is None:
            netmhc_filters = []
        if peptide_list_names is None:
            peptide_list_names = []
        for pln, hla, rank_cutoff in netmhc_filters:
            rank_cutoff = float(rank_cutoff)
            print('going to run netmhc')
            idNetMHC, pep_score_path = self.run_netmhc(pln, hla)
            row = self.db_session.query(tPipeDB.FilteredNetMHC).filter_by(idNetMHC = idNetMHC, RankCutoff=rank_cutoff).first()
            if row is None:
                row = tPipeDB.FilteredNetMHC(idNetMHC = idNetMHC, RankCutoff=rank_cutoff)
                self.db_session.add(row)
                self.db_session.commit()
            filtered_netmhc_rows.append(row)
            with open(os.path.join(self.project_path, pep_score_path), 'r') as f:
                tp = tempfile.NamedTemporaryFile(mode='w', delete=False)
                temp_files.append(tp)
                for line in f:
                    line_parts = line.split(',')
                    if len(line_parts) == 2:
                        rank = float(line_parts[1])
                        if rank <= rank_cutoff:
                            tp.write(line_parts[0] + '\n')
        files = []
        peptide_list_rows = []
        for pln in peptide_list_names:
            row = self.db_session.query(tPipeDB.PeptideList).filter_by(peptideListName=pln).first()
            if row:
                files.append(os.path.join(self.project_path, row.PeptideListPath))
                peptide_list_rows.append(row)
            else:
                raise NoSuchPeptideListError(pln)
        for x in temp_files:
            files.append(x.name)
            x.close()
        temp_fasta = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp_fasta.close()
        subprocess.run(['bash_scripts/join_peptides_to_fasta.sh'] + files + [temp_fasta.name])
        output_directory_name = str(uuid.uuid4().hex)
        output_directory_path = os.path.join(self.project_path, 'tide_indices', output_directory_name)
        while os.path.isfile(output_directory_path) or os.path.isdir(output_directory_path):
            output_directory_name = str(uuid.uuid4().hex)
            output_directory_path = os.path.join(self.project_path, 'tide_indices', output_directory_name)
        
        row = tide_index_runner.run_index_create_row(temp_fasta.name, output_directory_path, os.path.join('tide_indices', output_directory_name), 'index')
        row.TideIndexName = tide_index_name
        #now we must must set the relationships for peptidelists and filteredNetMHCs
        row.peptidelists = peptide_list_rows
        row.filteredNetMHCs = filtered_netmhc_rows
        self.db_session.add(row)
        self.db_session.commit()
        
        
    def run_netmhc(self, peptide_list_name, hla_name):
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
            call_netmhc(hla_name, os.path.join(self.project_path, peptide_list_row.PeptideListPath), os.path.join(self.project_path, 'NetMHC', netmhc_output_filename))
            parse_netmhc(os.path.join(self.project_path, 'NetMHC', netmhc_output_filename), os.path.join(self.project_path, 'NetMHC', netmhc_output_filename + '-parsed'))
            netmhc_row = tPipeDB.NetMHC(peptidelistID=peptide_list_row.idPeptideList, idHLA = hla_row.idHLA, NetMHCOutputPath=os.path.join('NetMHC', netmhc_output_filename), PeptideScorePath = os.path.join('NetMHC', netmhc_output_filename + '-parsed'))
            self.db_session.add(netmhc_row)
            self.db_session.commit()
            return (netmhc_row.idNetMHC, netmhc_row.PeptideScorePath)

    def generate_tide_index(self, peptide_list_names, netmhc_runs, tide_index_options):
        pass
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
        if (not ignore_operation_lock) and os.path.isfile(os.path.join(self.project_path, 'operation_lock')):
            raise OperationsLockedError()
        fasta_rows = self.db_session.query(tPipeDB.FASTA).all()
        for row in fasta_rows:
            path = row.FASTAPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                raise FASTAMissingError(row.idFASTA, row.Name, row.FASTAPath)
        peptide_list_rows = self.db_session.query(tPipeDB.PeptideList).all()
        for row in peptide_list_rows:
            path = row.PeptideListPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                raise PeptideListFileMissingError(row.idPeptideList, row.peptideListName, row.PeptideListPath)
        mgf_rows = self.db_session.query(tPipeDB.MGFfile).all()
        for row in mgf_rows:
            path = row.MGFPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                raise MGFFileMissingError(row.idMGFfile, row.MGFName, row.MGFPath)
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
            print(sys.exc_info()[0])
            print('There is a backup file: ' + os.path.join(self.project_path, 'backup.tar.gz') + ' That you can use to revert the changes to bring the project into a valid state. Just unpack it. If you didn\'t do anything unusualy, then please file a bug report')
            sys.exit(1)
        else:
            self.unlock_operations()
            os.remove(os.path.join(self.project_path, 'backup.tar.gz'))
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
            newpath = os.path.join(subfolder, path_tail + '-' + str(max_version + 1))
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
            subfolders = ['FASTA', 'peptides', 'NetMHC', 'tide_indices', 'MGF', 'tide_search_results', 'percolator_results', 'misc', 'tide_param_files']
            for subfolder in subfolders:
                os.mkdir(os.path.join(project_path, subfolder))
            return Project(project_path)



