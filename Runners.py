import DB
import sys
import os


import re
import shutil
import uuid
from fileFunctions import *
CRUX_BINARY = '/usr/bin/crux'
from Errors import *


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
        with open(os.path.join(project_path, 'tide_param_files', param_filename), 'w') as f:        
            for k, v in options.items():
                f.write(k + '=' + str(v) + '\n')
        spectra_file = os.path.join(project_path, mgf_row.MGFPath)
        index_filename = os.path.join(project_path, index_row.TideIndexPath)
        print('current working directory: ' + os.getcwd())
        command = [CRUX_BINARY, 'tide-search', '--output-dir', output_directory_tide, '--parameter-file', os.path.join(project_path, 'tide_param_files', param_filename), spectra_file, index_filename]
        try:
            p = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise TideSearchFailedError(' '.join(command))
        search_row = DB.TideSearch(tideindex = index_row, mgf=mgf_row, targetPath=os.path.join(output_directory_db, 'tide-search.target.txt'), decoyPath=os.path.join(output_directory_db, 'tide-search.decoy.txt'), paramsPath=os.path.join('tide_param_files', param_filename), logPath=os.path.join(output_directory_db, 'tide-search.log.txt'), SearchName=tide_search_row_name)
        return search_row

        
class TideIndexRunner:
    def __init__(self, tide_index_options):
        #tide_index_options is a dictionary.
        self.tide_index_options = tide_index_options


    @staticmethod
    def get_tide_index_options():
        return {'--clip-nterm-methionine': {'choices':['T', 'F']}, '--isotopic-mass': {'choices': ['average', 'mono']}, '--max-length': {'type': int}, '--max-mass': {'type':str}, '--min-length': {'type':int}, '--min-mass': {'type':str}, '--cterm-peptide-mods-spec': {'type': str}, '--max-mods': {'type': int}, '--min-mods': {'type':int}, '--mod-precision': {'type':int}, '--mods-spec': {'type': str}, '--nterm-peptide-mods-spec': {'type':str}, '--allow-dups': {'choices': ['T', 'F']}, '--decoy-format': {'choices': ['none', 'shuffle', 'peptide-reverse', 'protein-reverse'], 'default':'peptide-reverse'}, '--decoy-generator': {'type':str}, '--keep-terminal-aminos': {'choices': ['N', 'C', 'NC', 'none']}, '--seed': {'type':str}, '--custom-enzyme': {'type': str, 'default':'[Z]|[Z]'}, '--digestion': {'choices': ['full-digest', 'partial-digest', 'non-specific-digest']}, '--enzyme': {'choices': ['no-enzyme', 'trypsin', 'trypsin/p', 'chymotrypsin', 'elactase', 'clostripain', 'cyanogen-bromide', 'iodosobenzoat', 'proline-endopeptidase', 'staph-protease', 'asp-n', 'lys-c', 'lys-n', 'arg-c', 'glu-c', 'pepsin-a', 'elastase-trypsin-chymotrypsin', 'custom-enzyme'], 'default':'custom-enzyme'}, '--missed-cleavages': {'type': int}}
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
            p = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise TideIndexFailedError(' '.join(command))
        column_arguments = {}
        for k, v in self.tide_index_options.items():
            column_name = TideIndexRunner.convert_cmdline_option_to_column_name(k)
            if column_name:
                column_arguments[column_name] = v
        column_arguments['TideIndexPath'] = os.path.join(output_directory_db, index_filename)
        return DB.TideIndex(**column_arguments)

class AssignConfidenceRunner:
    def __init__(self, assign_confidence_options):
        self.assign_confidence_options = assign_confidence_options



    @staticmethod
    def get_assign_confidence_options():
        return {'--estimation-method': {'choices': ['mix-max', 'tdc', 'peptide-level']}, '--score': {'type': str}, '--sidak': {'choices': ['T', 'F']}, '--top-match-in': {'type': int}, '--combine-charge-states': {'choices': ['T', 'F']}, '--combine-modified-peptides': {'choices': ['T', 'F']}}

    @staticmethod
    def convert_cmdline_option_to_column_name(option):
        converter = {'estimation-method': 'estimation_method', 'score': 'score', 'sidak': sidak, 'top-match-in': 'top_match_in', 'combine-charge-states': 'combine_charge_states', 'combine-modified-peptides': 'combine_modified_peptides'}
        if option in converter:
            return converter[option]
        else:
            return None

    def run_assign_confidence_create_row(self, target_path, output_directory_tide, output_directory_db, assign_confidence_name, tide_search_row):
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
            p = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise AssignConfidenceFailedError(' '.join(command))
        column_arguments = {}
        for k, v in self.assign_confidence_options.items():
            column_name = AssignConfidenceRunner.convert_cmdline_option_to_column_name(k)
            if column_name:
                column_arguments[column_name] = v
        column_arguments['AssignConfidenceOutputPath'] = output_directory_db
        column_arguments['AssignConfidenceName'] = assign_confidence_name
        column_arguments['search'] = tide_search_row
        return DB.AssignConfidence(**column_arguments)


class PercolatorRunner:
    def __init__(self, param_file_path = False):
        if param_file_path:
            line_regex = re.compile('(?:#.*)|(\S+=\S+)|$')
            with open(param_file_path, 'r') as f:
                for line in f:
                    if line_regex.match(line) is None:
                        raise InvalidParameterLineError(line)
        self.param_file_path = param_file_path

    
    def run_percolator_create_row(self, target_path, output_directory_tide, output_directory_db, percolator_name, tide_search_row):
        command = [CRUX_BINARY, 'percolator']
        print('running percolator command from: ' + os.getcwd())
        column_arguments = {}
        if self.param_file_path:
            #copy the param file into output_directory_tide
            param_filename = os.path.basename(self.param_file_path)
            assert(len(param_filename) > 0)
            assert(param_filename not in ['percolator.target.proteins.txt', 'percolator.decoy.proteins.txt', 'percolator.target.peptides.txt', 'percolator.decoy.peptides.txt', 'percolator.target.psms.txt', 'percolator.decoy.psms.txt', 'percolator.params.txt', 'percolator.pep.xml', 'percolator.mzid', 'percolator.log.txt'])
            copy_path = shutil.copy2(self.param_file_path, output_directory_tide)
            command.append('--parameter-file')
            command.append(copy_path)
            column_arguments['inputParamFilePath'] = os.path.join(output_directory_db, param_filename)
        command.append('--output-dir')
        command.append(output_directory_tide)
        command.append(target_path)

        print('command')
        print(' '.join(command))
        try:
            p = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise PercolatorFailedError(' '.join(command))
        column_arguments['PercolatorOutputPath'] = output_directory_db
        column_arguments['PercolatorName'] = percolator_name
        column_arguments['search'] = tide_search_row
        return DB.Percolator(**column_arguments)
