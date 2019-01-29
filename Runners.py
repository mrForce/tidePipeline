import DB
import sys
import os
import Parsers
import BashScripts
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
        self.project_path = project_path
        self.param_file_row = param_file_row
        self.crux_binary = crux_binary
    @staticmethod
    def get_tide_search_options():
        return {'--mod-precision': {'type':int}, '--auto-precursor-window': {'choices': ['false', 'warn', 'fail']}, '--max-precursor-charge': {'type': int}, '--precursor-window': {'type': float}, '--precursor-window-type': {'choices': ['mass', 'mz', 'ppm']}, '--auto-mz-bin-width': {'choices': ['false', 'warn', 'fail']}, '--compute-sp': {'choices': ['T', 'F']}, '--deisotope': {'type': float}, '--exact-p-value': {'choices':['T', 'F']}, '--isotope-error': {'type': str}, '--min-peaks': {'type': int}, '--mz-bin-offset': {'type': float}, '--mz-bin-width': {'type': float}, '--peptide-centric-search': {'choices': ['T', 'F']}, '--score-function': {'choices': ['xcorr', 'residue-evidence', 'both']}, '--fragment-tolerance': {'type': float}, '--evidence-granularity': {'type': int}, '--remove-precursor-peak': {'choices': ['T', 'F']}, '--remove-precursor-tolerance': {'type': float}, '--scan-number': {'type': str}, '--skip-processing': {'choices': ['T', 'F']}, '--spectrum-charge': {'choices': ['1', '2', '3', 'all']}, '--spectrum-max-mz': {'type': float}, '--spectrum-min-mz': {'type': float}, '--use-flanking-peaks': {'choices': ['T', 'F']}, '--use-neutral-loss-peaks': {'choices': ['T', 'F']}, '--num-threads': {'type': int}, '--pm-charge': {'type': int}, '--pm-max-frag-mz': {'type': float}, '--pm-max-precursor-delta-ppm': {'type': float}, '--pm-max-precursor-mz': {'type': float}, '--pm-max-scan-seperation': {'type': int}, '--pm-min-common-frag-peaks': {'type': int}, '--pm-min-frag-mz': {'type': float}, '--pm-min-peak-pairs': {'type': int}, '--pm-min-precursor-mz': {'type': float}, '--pm-min-scan-frag-peaks': {'type': int}, '--pm-pair-top-n-frag-peaks': {'type': int}, '--pm-top-n-frag-peaks': {'type': int}, '--concat': {'choices': ['T', 'F']}, '--file-column': {'choices': ['T', 'F']}, '--fileroot': {'type': str}, '--mass-precision': {'type': int}, '--mzid-output': {'choices': ['T', 'F']}, '--precision': {'type': int}, '--spectrum-parser': {'choices': ['pwiz', 'mstoolkit']}, '--store-spectra': {'type': str}, '--top-match': {'type': int}, '--use-z-line': {'choices': ['T', 'F']}}

    #change the options here
    def run_search_create_row(self, mgf_row, index_row, output_directory_tide, output_directory_db, tide_search_row_name, partOfIterativeSearch = False):
        spectra_file = os.path.join(self.project_path, mgf_row.MGFPath)
        index_filename = os.path.join(self.project_path, index_row.TideIndexPath)
        print('current working directory: ' + os.getcwd())
        params = {}
        if self.param_file_row:
            param_file_path = os.path.join(self.project_path, self.param_file_row.Path)
            params = Parsers.parseTideParamFile(param_file_path)
            command = [self.crux_binary, 'tide-search', '--output-dir', output_directory_tide, '--parameter-file', param_file_path, spectra_file, index_filename, '--pin-output', 'T']
        else:        
            command = [self.crux_binary, 'tide-search', '--output-dir', output_directory_tide, spectra_file, index_filename, '--pin-output', 'T']
        try:
            p = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise TideSearchFailedError(' '.join(command))
        if 'concat' in params:
            assert(params['concat'] in ['true', 'false'])
            if params['concat'] == 'true':
                search_row = DB.TideSearch(tideindex = index_row, mgf=mgf_row, targetPath=os.path.join(output_directory_db, 'tide-search.pin'), parameterFile = self.param_file_row, concat = True, logPath=os.path.join(output_directory_db, 'tide-search.log.txt'), SearchName=tide_search_row_name, partOfIterativeSearch = partOfIterativeSearch)
                return search_row
        decoy_pin_path = os.path.join(output_directory_db, 'tide-search.decoy.pin') if os.path.exists(os.path.join(output_directory_tide, 'tide-search.decoy.pin')) else None
        target_pin_path = os.path.join(output_directory_db, 'tide-search.target.pin') if os.path.exists(os.path.join(output_directory_tide, 'tide-search.target.pin')) else None
        log_path = os.path.join(output_directory_db, 'tide-search.log.txt') if os.path.exists(os.path.join(output_directory_tide, 'tide-search.log.txt')) else None
        search_row = DB.TideSearch(tideindex = index_row, mgf=mgf_row, targetPath=target_pin_path, decoyPath=decoy_pin_path, parameterFile = self.param_file_row, logPath=log_path, SearchName=tide_search_row_name, partOfIterativeSearch = partOfIterativeSearch)
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

class MSGFPlusTrainingRunner:
    converter = {'m': 'fragmentationMethod', 'inst': 'instrument', 'e': 'enzyme'}
    def __init__(self, project_path, jar_file_location):
        self.project_path = project_path
        self.jar_file_location = jar_file_location

    @classmethod
    def convert_cmdline_option_to_column_name(cls, option):
        if option in cls.converter:
            return cls.converter[option]
        else:
            return None
    def run_training_create_row(self, mgf_row, search_row, training_name, output_directory, memory = None):
        mgf_location = os.path.join(self.project_path, mgf_row.MGFPath)
        mgf_folder = os.path.dirname(mgf_location)
        mzid_location = os.path.join(self.project_path, search_row.resultFilePath)
        mzid_folder = os.path.dirname(mzid_location)
        memory_string = '-Xmx3500M'
        if memory:
            memory_string = '-Xmx' + str(memory) + 'M'
        command = ['java', memory_string, '-cp', self.jar_file_location, 'edu.ucsd.msjava.ui.ScoringParamGen', '-i', mzid_folder, '-d', mgf_folder, '-m', str(mgf_row.fragmentationMethod), '-inst', str(mgf_row.instrument), '-e', str(mgf_row.enzyme)]

        """
        The way MSGF+ specifies the param file is a bit funky, so we're going to have to work around it.


        Need to capture stdout, and parse it to extract what's after 'Output file name: '. Then, move that file into the project.

        Then, before doing a search, I need to copy the param file to the params folder in the MSGF+ installation, and specify the fragmentation, instrument and enzyme in the command line. When the search is complete, I need to delete the file. 
        """
        param_path = None
        try:
            print('command: ' +  ' '.join([str(x) for x in command]))
            with tempfile.TemporaryFile() as f:                
                p = subprocess.call([str(x) for x in command], stdout=f, stderr=sys.stderr)
                f.seek(0)
                regex = re.compile('Output file name:\s*(?P<path>.*)')
                for x in f:
                    line = x.decode('utf-8', 'ignore')
                    match = regex.match(line)
                    if match:
                        param_path = match.group('path')
                        break
                if param_path is None:
                    f.seek(0)
                    for x in f:
                        print(x.strip())                        
                    raise NoPathInMSGFPlusTrainingOutput()            
        except subprocess.CalledProcessError:
            raise MSGFPlusTrainingFailedError(' '.join(command))
        shutil.move(param_path, os.path.join(self.project_path, output_directory))
        column_args = {'trainingName': training_name, 'paramFileLocation': storage_directory, 'MSGFPlusSearch': search_row, 'MGF': mgf_row, 'fragmentationMethod': mgf_row.fragmentationMethod, 'instrument': mgf_row.instrument, 'enzyme': mgf_row.enzyme}
        training_row = DB.MSGFPlusTrainingParams(**column_args)
        return training_row



class MSGFPlusSearchRunner:
    converter = {'t': 'ParentMassTolerance', 'ti': 'IsotopeErrorRange', 'thread': 'NumOfThreads', 'm': 'FragmentationMethodID', 'inst': 'InstrumentID', 'minLength': 'minPepLength', 'maxLength': 'maxPepLength', 'minCharge': 'minPrecursorCharge', 'maxCharge': 'maxPrecursorCharge', 'ccm':  'ccm', 'e': 'EnzymeID'}
    def __init__(self, args, jar_file_location):
        self.jar_file_location = jar_file_location
        self.args = args
    @staticmethod
    def get_search_options():
        return {'--t': {'type':str, 'help': 'ParentMassTolerance'}, '--ti': {'type': str, 'help': 'IsotopeErrorRange'}, '--thread': {'type': str, 'help': 'NumThreads'}, '--m': {'type': str, 'help':'FragmentMethodID'}, '--inst': {'type': str, 'help': 'MS2DetectorID'}, '--minLength': {'type': int, 'help': 'MinPepLength'}, '--maxLength': {'type': int, 'help': 'MaxPepLength'}, '--minCharge': {'type': int, 'help': 'MinCharge'}, '--maxCharge': {'type': int, 'help': 'MaxCharge'}, '--ccm': {'type': str, 'help': 'ChargeCarrierMass'}, '--e': {'type': int, 'help': 'enzymeID'}}
    @classmethod
    def convert_cmdline_option_to_column_name(cls, option):
        if option in cls.converter:
            return cls.converter[option]
        else:
            return None
    #change the options here
    def run_search_create_row(self, mgf_row, index_row, modifications_file_row, output_directory, project_path, search_row_name, memory=None, partOfIterativeSearch = False, training_param_row = None):        
        #output directory relative to the project path
        mgf_location = os.path.join(project_path, mgf_row.MGFPath)
        print('mgf location: ' + mgf_location)
        fasta_index_location = os.path.join(project_path, index_row.MSGFPlusIndexPath)
        memory_string = '-Xmx3500M'
        if memory:
            memory_string = '-Xmx' + str(memory) + 'M'
        if index_row.netmhc_decoys or index_row.customDecoys:
            tda = 0
        else:
            tda = 1
        enzyme = '9'
        if index_row.fasta:
            #then by default use unspecific enzyme
            print('index comes from FASTA. Using unspecific enzyme')
            enzyme = '0'
        else:
            if mgf_row.enzyme != 8:
                enzyme = str(mgf_row.enzyme - 1)
        msgf_param_folder = None
        if training_param_row:
            #params folder is in current working directory
            msgf_param_folder = os.path.join(os.getcwd(), 'params')
            if not os.path.isdir(msgf_param_folder):
                os.mkdir(msgf_param_folder)
            shutil.copy(os.path.join(project_path, training_param_row.paramFileLocation), msgf_param_folder)
        
        command = ['java', memory_string, '-jar', self.jar_file_location, '-ignoreMetCleavage', '1', '-s', mgf_location, '-d', fasta_index_location, '-tda', tda, '-o', os.path.join(project_path, output_directory, 'search.mzid'), '-addFeatures', '1']
        column_args = {'index': index_row, 'mgf': mgf_row, 'SearchName': search_row_name, 'resultFilePath': os.path.join(output_directory, 'search.mzid'), 'partOfIterativeSearch': partOfIterativeSearch}
        if modifications_file_row:
            modification_file_location = os.path.join(project_path, modifications_file_row.MSGFPlusModificationFilePath)
            command.append('-mod')
            command.append(modification_file_location)
            column_args['modificationFile'] = modifications_file_row
        column_args['addFeatures'] = 1
        default_args = {'e': enzyme, 'm': str(mgf_row.fragmentationMethod + 1), 'inst': str(mgf_row.instrument)}

        """
        To clarify here: because the args are appended to default_args, if there are two conflicting arguments (such as enzyme), the one given by the user will be used when converted to a dictionary.
        """
        for key, value in dict(list(default_args.items()) + list(self.args.items())).items():
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
            print('command: ' +  ' '.join([str(x) for x in command]))
            p = subprocess.call([str(x) for x in command], stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            raise MSGFPlusSearchFailedError(' '.join(command))


        search_row = DB.MSGFPlusSearch(**column_args)
        return search_row


class MSGFPlusIndexRunner:
    def __init__(self, jar_file_location):
        self.jar_file_location = jar_file_location
    #netmhc_decoys should either be None or a list of BashScripts.ParsedNetMHC objects
    def run_index_create_row(self, fasta_path, output_directory_path, project_path, memory=None, *, netmhc_decoys = None, decoy_type=None):
        #copy the FASTA file to output_directory_path
        fasta_head, fasta_tail = os.path.split(fasta_path)
        new_fasta_path = ''
        if fasta_tail.endswith('.fasta'):
            new_fasta_path = shutil.copy(fasta_path, output_directory_path)
        else:
            #I did this since the index builder needs the FASTA filename to end with .fasta
            new_fasta_path = shutil.copy(fasta_path, os.path.join(output_directory_path, fasta_tail + '.fasta'))
        new_fasta_head, new_fasta_tail = os.path.split(new_fasta_path)
        if netmhc_decoys:
            BashScripts.netMHCDecoys(netmhc_decoys, os.path.abspath(fasta_path), os.path.abspath(new_fasta_path))
            tda = 0
        elif decoy_type:
            BashScripts.generateDecoys(os.path.abspath(fasta_path), os.path.abspath(new_fasta_path), decoy_type)            
            tda = 0
        current_path = os.getcwd()
        os.chdir(output_directory_path)
        memory_string = '-Xmx3500M'
        if memory:
            memory_string = '-Xmx' + str(memory) + 'M'
        tda = 2
        
        command = ['java', memory_string, '-cp', self.jar_file_location, 'edu.ucsd.msjava.msdbsearch.BuildSA', '-d', new_fasta_tail, '-tda', str(tda)]
        print('index command: ' + ' '.join(command))
        print('ran in: ' + str(os.getcwd()))
        try:
            p = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            assert(False)
            #raise MSGFPlusIndexFailedError(' '.join(command))
        os.chdir(current_path)
        customDecoys = 0
        if decoy_type:
            customDecoys = 1
        if netmhc_decoys:
            return (DB.MSGFPlusIndex(tda=str(tda), customDecoys = customDecoys, netmhc_decoys=list(netmhc_decoys.keys())), new_fasta_tail)
        else:
            return (DB.MSGFPlusIndex(tda=str(tda), customDecoys = customDecoys), new_fasta_tail)



class TideIndexRunner:
    converter = {'clip-nterm-methionine': 'clip_nterm_methionine', 'isotopic-mass': 'isotopic_mass', 'max-length': 'max_length', 'max-mass': 'max_mass', 'min-length': 'min_length', 'min-mass': 'min_mass', 'cterm-peptide-mods-spec': 'cterm_peptide_mods_spec', 'max-mods': 'max_mods', 'min-mods':'min_mods', 'mod-precision': 'mod_precision', 'mods-spec': 'mods_spec', 'nterm-peptide-mods-spec': 'nterm_peptide_mods_spec', 'allow-dups': 'allow_dups', 'decoy-format': 'decoy_format', 'decoy-generator': 'decoy_generator', 'keep-terminal-aminos': 'keep_terminal_aminos', 'seed': 'seed', 'custom-enzyme': 'custom_enzyme', 'digestion': 'digestion', 'enzyme': 'enzyme', 'missed-cleavages': 'missed_cleavages'}
    def __init__(self, tide_index_options, crux_binary, project_path, param_file_row = None):
        #tide_index_options is a dictionary.
        self.project_path = project_path
        self.param_file_row = param_file_row
        self.tide_index_options = tide_index_options
        self.crux_binary = crux_binary


    @staticmethod
    def get_tide_index_options():
        return {'--clip-nterm-methionine': {'choices':['T', 'F']}, '--isotopic-mass': {'choices': ['average', 'mono']}, '--max-length': {'type': int}, '--max-mass': {'type':str}, '--min-length': {'type':int}, '--min-mass': {'type':str}, '--cterm-peptide-mods-spec': {'type': str}, '--max-mods': {'type': int}, '--min-mods': {'type':int}, '--mod-precision': {'type':int}, '--mods-spec': {'type': str}, '--nterm-peptide-mods-spec': {'type':str}, '--allow-dups': {'choices': ['T', 'F']}, '--decoy-format': {'choices': ['none', 'shuffle', 'peptide-reverse', 'protein-reverse']}, '--decoy-generator': {'type':str}, '--keep-terminal-aminos': {'choices': ['N', 'C', 'NC', 'none']}, '--seed': {'type':str}, '--custom-enzyme': {'type': str, 'default':'[Z]|[Z]'}, '--digestion': {'choices': ['full-digest', 'partial-digest', 'non-specific-digest']}, '--enzyme': {'choices': ['no-enzyme', 'trypsin', 'trypsin/p', 'chymotrypsin', 'elactase', 'clostripain', 'cyanogen-bromide', 'iodosobenzoat', 'proline-endopeptidase', 'staph-protease', 'asp-n', 'lys-c', 'lys-n', 'arg-c', 'glu-c', 'pepsin-a', 'elastase-trypsin-chymotrypsin', 'custom-enzyme'], 'default':'custom-enzyme'}, '--missed-cleavages': {'type': int}}
    @classmethod
    def convert_cmdline_option_to_column_name(cls, option):        
        if option in cls.converter:
            return cls.converter[option]
        else:
            return None
    def run_index_create_row(self, fasta_path, output_directory_tide, output_directory_db, index_filename, *, netmhc_decoys = None, decoy_type = None):
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
        os.mkdir(output_directory_tide)
        command.append('--overwrite')
        command.append('T')        
        if netmhc_decoys or decoy_type:
            new_fasta_path = os.path.join(output_directory_tide, 'targets_and_decoys.fasta')
            shutil.copyfile(fasta_path, os.path.abspath(new_fasta_path))
            decoy_format = 'none'
            if netmhc_decoys:
                assert(decoy_type is None)
                BashScripts.netMHCDecoys(netmhc_decoys, os.path.abspath(fasta_path), os.path.abspath(new_fasta_path), decoy_prefix = '>decoy_')
                fasta_path= new_fasta_path
            elif decoy_type:
                assert(netmhc_decoys is None)
                if decoy_type == 'tide_shuffle':
                    decoy_format = 'shuffle'
                elif decoy_type == 'tide_reverse':
                    decoy_format = 'peptide-reverse'
                else:                    
                    BashScripts.generateDecoys(os.path.abspath(fasta_path), os.path.abspath(new_fasta_path), decoy_type, decoy_prefix='>decoy_')
                    fasta_path= new_fasta_path
            command.append('--decoy-format')
            command.append(decoy_format)
            

            
        command.append(fasta_path)
        command.append(os.path.join(output_directory_tide, index_filename))
        print('command')
        print(command)
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
        if netmhc_decoys:
            column_arguments['netmhc_decoys'] = list(netmhc_decoys.keys())
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
    def __init__(self, crux_binary, project_path, param_file_row = None):
        self.crux_binary = crux_binary
        self.param_file_row = param_file_row
        self.project_path = project_path

    def run_percolator_create_row(self, target_path, output_directory_tide, output_directory_db, percolator_name, tide_search_row, partOfIterativeSearch = False):
        assert(target_path)
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

