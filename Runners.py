import DB
import sys
import os
import Parsers

import re
import shutil
import uuid
from fileFunctions import *

from Errors import *

class MSGF2PinRunner:
    def __init__(self, msgf2pin_binary, unimodXMLLocation):
        self.msgf2pin_binary = msgf2pin_binary
        self.unimodXMLLocation = unimodXMLLocation
    def runConversion(self, mzid_location, output_pin_location, fasta_files, decoy_pattern):
        command = [self.msgf2pin_binary, mzid_location, '-o', output_pin_location, '-F', ','.join(fasta_files), '-e', 'no_enzyme', '-r', '-u', self.unimodXMLLocation, '-P', decoy_pattern]
        print('going to run MSGF2pin conversion')
        print(command)
        try:
            p = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise MSGF2PinFailedError(' '.join(command))

class TideSearchRunner:
    def __init__(self, crux_binary, project_path, param_file_row = None):
        self.param_file_row = param_file_row
        self.project_path = project_path
        self.crux_binary = crux_binary
    @staticmethod
    def get_tide_search_options():
        return {'--mod-precision': {'type':int}, '--auto-precursor-window': {'choices': ['false', 'warn', 'fail']}, '--max-precursor-charge': {'type': int}, '--precursor-window': {'type': float}, '--precursor-window-type': {'choices': ['mass', 'mz', 'ppm']}, '--auto-mz-bin-width': {'choices': ['false', 'warn', 'fail']}, '--compute-sp': {'choices': ['T', 'F']}, '--deisotope': {'type': float}, '--exact-p-value': {'choices':['T', 'F']}, '--isotope-error': {'type': str}, '--min-peaks': {'type': int}, '--mz-bin-offset': {'type': float}, '--mz-bin-width': {'type': float}, '--peptide-centric-search': {'choices': ['T', 'F']}, '--score-function': {'choices': ['xcorr', 'residue-evidence', 'both']}, '--fragment-tolerance': {'type': float}, '--evidence-granularity': {'type': int}, '--remove-precursor-peak': {'choices': ['T', 'F']}, '--remove-precursor-tolerance': {'type': float}, '--scan-number': {'type': str}, '--skip-processing': {'choices': ['T', 'F']}, '--spectrum-charge': {'choices': ['1', '2', '3', 'all']}, '--spectrum-max-mz': {'type': float}, '--spectrum-min-mz': {'type': float}, '--use-flanking-peaks': {'choices': ['T', 'F']}, '--use-neutral-loss-peaks': {'choices': ['T', 'F']}, '--num-threads': {'type': int}, '--pm-charge': {'type': int}, '--pm-max-frag-mz': {'type': float}, '--pm-max-precursor-delta-ppm': {'type': float}, '--pm-max-precursor-mz': {'type': float}, '--pm-max-scan-seperation': {'type': int}, '--pm-min-common-frag-peaks': {'type': int}, '--pm-min-frag-mz': {'type': float}, '--pm-min-peak-pairs': {'type': int}, '--pm-min-precursor-mz': {'type': float}, '--pm-min-scan-frag-peaks': {'type': int}, '--pm-pair-top-n-frag-peaks': {'type': int}, '--pm-top-n-frag-peaks': {'type': int}, '--concat': {'choices': ['T', 'F']}, '--file-column': {'choices': ['T', 'F']}, '--fileroot': {'type': str}, '--mass-precision': {'type': int}, '--mzid-output': {'choices': ['T', 'F']}, '--precision': {'type': int}, '--spectrum-parser': {'choices': ['pwiz', 'mstoolkit']}, '--store-spectra': {'type': str}, '--top-match': {'type': int}, '--use-z-line': {'choices': ['T', 'F']}}

    #change the options here
    def run_search_create_row(self, mgf_row, index_row, output_directory_tide, output_directory_db, tide_search_row_name, partOfIterativeSearch = False):    
        spectra_file = os.path.join(self.project_path, mgf_row.MGFPath)
        index_filename = os.path.join(self.project_path, index_row.TideIndexPath)
        print('current working directory: ' + os.getcwd())
        if self.param_file_row:
            param_file_path = os.path.join(self.project_path, self.param_file_row.Ptah)
            command = [self.crux_binary, 'tide-search', '--output-dir', output_directory_tide, '--parameter-file', param_file_path, spectra_file, index_filename]
        else:        
            command = [self.crux_binary, 'tide-search', '--output-dir', output_directory_tide, spectra_file, index_filename]
        try:
            p = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise TideSearchFailedError(' '.join(command))
        search_row = DB.TideSearch(tideindex = index_row, mgf=mgf_row, targetPath=os.path.join(output_directory_db, 'tide-search.target.txt'), decoyPath=os.path.join(output_directory_db, 'tide-search.decoy.txt'), parameterFile = self.param_file_row, logPath=os.path.join(output_directory_db, 'tide-search.log.txt'), SearchName=tide_search_row_name, partOfIterativeSearch = partOfIterativeSearch)
        return search_row

class MaxQuantSearchRunner:
    def __init__(self, exe_file_location):
        self.exe_file_location = exe_file_location

    def run_search_create_row(self, raw_row, fasta_path, param_file_row, output_directory, project_path, search_row_name, fdr):
        param_file_path = os.path.join(project_path, param_file_row.Path)
        custom_param_file_path = os.path.join(project_path, output_directory, os.path.split(param_file_row.Path)[1])
        parser = Parsers.CustomizableMQParamParser(param_file_path)
        parser.set_fasta(fasta_path)
        parser.set_raw(os.path.abspath(os.path.join(project_path, raw_row.RAWPath)))
        parser.set_output_location(os.path.abspath(os.path.join(project_path, output_directory)))
        parser.set_peptide_fdr(fdr)
        parser.write_mq(custom_param_file_path)
        parser.set_peptide_fdr(fdr)
        command = ['mono', self.exe_file_location, os.path.abspath(custom_param_file_path)]
        print('About to run mono command. Current location: ' + os.getcwd())
        try:
            p = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise MaxQuantSearchFailedError(' '.join(command))
        row = DB.MaxQuantSearch(raw = raw_row, Path = output_directory, SearchName = search_row_name, fdr=str(fdr))
        return row
class MSGFPlusSearchRunner:
    def __init__(self, args, jar_file_location):
        self.jar_file_location = jar_file_location
        self.args = args
    @staticmethod
    def get_search_options():
        return {'--t': {'type':str, 'help': 'ParentMassTolerance'}, '--ti': {'type': str, 'help': 'IsotopeErrorRange'}, '--thread': {'type': str, 'help': 'NumThreads'}, '--m': {'type': str, 'help':'FragmentMethodID'}, '--inst': {'type': str, 'help': 'MS2DetectorID'}, '--minLength': {'type': int, 'help': 'MinPepLength'}, '--maxLength': {'type': int, 'help': 'MaxPepLength'}, '--minCharge': {'type': int, 'help': 'MinCharge'}, '--maxCharge': {'type': int, 'help': 'MaxCharge'}, '--ccm': {'type': str, 'help': 'ChargeCarrierMass'}}
    @staticmethod
    def convert_cmdline_option_to_column_name(option):
        options = {'t': 'ParentMassTolerance', 'ti': 'IsotopeErrorRange', 'thread': 'NumOfThreads', 'm': 'FragmentationMethodID', 'inst': 'InstrumentID', 'minLength': 'minPepLength', 'maxLength': 'maxPepLength', 'minCharge': 'minPrecursorCharge', 'maxCharge': 'maxPrecursorCharge', 'ccm':  'ccm'}
        if option in options:
            return options[option]
        else:
            return None
    #change the options here
    def run_search_create_row(self, mgf_row, index_row, modifications_file_row, output_directory, project_path, search_row_name, memory=None, partOfIterativeSearch = False):
        #output directory relative to the project path
        mgf_location = os.path.join(project_path, mgf_row.MGFPath)
        print('mgf location: ' + mgf_location)
        fasta_index_location = os.path.join(project_path, index_row.MSGFPlusIndexPath)
        memory_string = '-Xmx3500M'
        if memory:
            memory_string = '-Xmx' + str(memory) + 'M'
        command = ['java', memory_string, '-jar', self.jar_file_location, '-s', mgf_location, '-d', fasta_index_location, '-e', '9', '-tda', '1', '-o', os.path.join(project_path, output_directory, 'search.mzid'), '-addFeatures', '1']
        column_args = {'index': index_row, 'mgf': mgf_row, 'SearchName': search_row_name, 'resultFilePath': os.path.join(project_path, output_directory, 'search.mzid'), 'partOfIterativeSearch': partOfIterativeSearch}
        if modifications_file_row:
            modification_file_location = os.path.join(project_path, modifications_file_row.MSGFPlusModificationFilePath)
            command.append('-mod')
            command.append(modification_file_location)
            column_args['modificationFile'] = modifications_file_row
        column_args['addFeatures'] = 1
        for key, value in self.args.items():
            if key and value:
                command.append('-' + key)
                command.append(str(value))
                column_name = MSGFPlusSearchRunner.convert_cmdline_option_to_column_name(key)
                if column_name:
                    column_args[column_name] = str(value)
                else:
                    print('key: ' + key)
                    assert(column_name)

        try:
            p = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise MSGFPlusSearchFailedError(' '.join(command))
        
        search_row = DB.MSGFPlusSearch(**column_args)
        return search_row


class MSGFPlusIndexRunner:
    def __init__(self, jar_file_location):
        self.jar_file_location = jar_file_location
    def run_index_create_row(self, fasta_path, output_directory_path, memory=None):
        #copy the FASTA file to output_directory_path
        fasta_head, fasta_tail = os.path.split(fasta_path)
        new_fasta_path = ''
        if fasta_tail.endswith('.fasta'):
            new_fasta_path = shutil.copy(fasta_path, output_directory_path)
        else:
            new_fasta_path = shutil.copy(fasta_path, os.path.join(output_directory_path, fasta_tail + '.fasta'))
        new_fasta_head, new_fasta_tail = os.path.split(new_fasta_path)
        current_path = os.getcwd()
        os.chdir(output_directory_path)
        memory_string = '-Xmx3500M'
        if memory:
            memory_string = '-Xmx' + str(memory) + 'M'
        command = ['java', memory_string, '-cp', self.jar_file_location, 'edu.ucsd.msjava.msdbsearch.BuildSA', '-d', new_fasta_tail, '-tda', '2']
        print('index command: ' + ' '.join(command))
        print('ran in: ' + str(os.getcwd()))
        try:
            p = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            assert(False)
            #raise MSGFPlusIndexFailedError(' '.join(command))
        os.chdir(current_path)
        return (DB.MSGFPlusIndex(tda=2), new_fasta_tail)



class TideIndexRunner:
    def __init__(self, tide_index_options, crux_binary, project_path, param_file_row = False):
        #tide_index_options is a dictionary.
        self.project_path = project_path
        self.param_file_row = param_file_row 
        self.tide_index_options = tide_index_options
        self.crux_binary = crux_binary

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
        command = [self.crux_binary, 'tide-index']
        for k,v in self.tide_index_options.items():
            if k and v:
                command.append('--' + k)
                command.append(v)
        if self.param_file_row:
            command.append('--parameter-file')
            command.append(os.path.join(self.project_path, self.param_file_row.Path))
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
        if self.param_file_row:
            column_arguments['parameterFile'] = self.param_file_row
        return DB.TideIndex(**column_arguments)

class AssignConfidenceRunner:
    def __init__(self, crux_binary, project_path, param_file_row = None):
        self.project_path = project_path
        self.param_file_row = param_file_row
        self.crux_binary = crux_binary


    @staticmethod
    def get_assign_confidence_options():
        return {'--estimation-method': {'choices': ['mix-max', 'tdc', 'peptide-level']}, '--score': {'type': str}, '--sidak': {'choices': ['T', 'F']}, '--top-match-in': {'type': int}, '--combine-charge-states': {'choices': ['T', 'F']}, '--combine-modified-peptides': {'choices': ['T', 'F']}}

        
    @staticmethod
    def convert_cmdline_option_to_column_name(option):
        converter = {'estimation-method': 'estimation_method', 'score': 'score', 'sidak': 'sidak', 'top-match-in': 'top_match_in', 'combine-charge-states': 'combine_charge_states', 'combine-modified-peptides': 'combine_modified_peptides'}
        if option in converter:
            return converter[option]
        else:
            return None

    def run_assign_confidence_create_row(self, target_path, output_directory_tide, output_directory_db, assign_confidence_name, tide_search_row, partOfIterativeSearch = False):
        #first, need to create the tide-index command
        command = [self.crux_binary, 'assign-confidence']
        if self.param_file_row:
            command.append('--parameter-file')
            command.append(os.path.join(self.project_path, self.param_file_row.Path))
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
        """
        for k, v in self.assign_confidence_options.items():
            column_name = AssignConfidenceRunner.convert_cmdline_option_to_column_name(k)
            if column_name:
                column_arguments[column_name] = v
        """
        if self.param_file_row:
            column_arguments['parameterFile'] = self.param_file_row
        column_arguments['AssignConfidenceOutputPath'] = output_directory_db
        column_arguments['AssignConfidenceName'] = assign_confidence_name
        column_arguments['searchbase'] = tide_search_row
        column_arguments['partOfIterativeSearch'] = partOfIterativeSearch
        return DB.AssignConfidence(**column_arguments)


class PercolatorRunner:
    def __init__(self, crux_binary, project_path, param_file_row = False):
        self.param_file_row = param_file_row
        self.crux_binary = crux_binary
        self.project_path = project_path
    
    def run_percolator_create_row(self, target_path, output_directory_tide, output_directory_db, percolator_name, tide_search_row, partOfIterativeSearch = False):
        command = [self.crux_binary, 'percolator']
        print('running percolator command from: ' + os.getcwd())
        column_arguments = {}
        if self.param_file_row:
            command.append('--parameter-file')
            command.append(os.path.join(self.project_path, self.param_file_row.Path))
            column_arguments['parameterFile'] = self.param_file_row
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
        column_arguments['searchbase'] = tide_search_row
        column_arguments['partOfIterativeSearch'] = partOfIterativeSearch
        return DB.Percolator(**column_arguments)

