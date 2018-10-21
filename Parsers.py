import xml.etree.ElementTree as ET
import re
import csv
from xml.sax.saxutils import unescape
import sys
from enum import Enum
from abc import ABC
class PINType(Enum):
    tide=1
    msgf=1

    """
    An iterator that yields a tuple of the form (is_target_row, row), where is_target_row is a boolean that is True if the row is a target row, and False if the row is a decoy row.
    """
def readSinglePIN(pin_path, target_checker_fn, *, skipe_defaults_row = True, restkey='Proteins'):    
    with open(pin_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t', restkey=restkey)
        if skip_defaults_row:
            self.reader.__next__()
        for row in reader:
            is_target_row = False
            if target_checker_fn(row):
                is_target_row = True
            yield (is_target_row, row)

def readDualPIN(target_pin_path, decoy_pin_path, *, skipe_defaults_row = True, restkey='Proteins'):    
    with open(target_pin_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t', restkey=restkey)
        for row in reader:
            yield (True, row)
    with open(decoy_pin_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t', restkey=restkey)
        for row in reader:
            yield (False, row)



class PINParser:
    #pin_row_generator is either a readDualPIN or readSinglePIN generator.
    def __init__(self, pin_row_generator, pin_type, min_peptide_length, max_peptide_length):
        self.path = path
        self.ranks = {}
        self.pin_type = pin_type
        self.min_peptide_length = min_peptide_length
        self.max_peptide_length = max_peptide_length
        self.target_rows = []
        self.decoy_rows = []
        for is_target, row in pin_row_generator:
            if is_target:
                self.target_rows.append(row)
            else:
                self.decoy_rows.append(row)
        
    @staticmethod
    def parse_peptide(peptide, length):
        #remove anything but the peptide, including PTMs. 
        matches = re.findall('([A-Za-z]+)(?:\[[+-\.\d]+\])?', peptide)
        cleaned_peptide = ''.join(matches)
        assert(len(cleaned_peptide) == length)
        return cleaned_peptide

    def _get_peptides(self, targets):
        peptides = set()
        if targets:
            for row in self.target_rows:
                peptides.add(PINParser.parse_peptide(row['Peptide'], int(row['PepLen'])))
        else:
            for row in self.decoy_rows:
                peptides.add(PINParser.parse_peptide(row['Peptide'], int(row['PepLen'])))
        return peptides
    """
    To be completely clear, these are the target peptides found in the PSMs in the PIN file.
    """
    def get_target_peptides(self):
        return self._get_peptides(True)
    def get_decoy_peptides(self):
        return self._get_peptides(False)

    def set_netmhc_ranks(self, header, target_ranks, decoy_ranks):
        self.ranks[header] = {'targets': target_ranks, 'decoys': decoy_ranks}
    def write(self, output_path):
        self._insert_netmhc_ranks(output_path)
    @staticmethod
    def msgf_is_target(row):
        #pass this as target_checker_fn if parsing MSGF+ output.
        assert(isinstance(row['Proteins'], list) or isinstance(row['Proteins'], tuple) or isinstance(row['Proteins'], str))
        if isinstance(row['Proteins'], list) or isinstance(row['Proteins'], tuple):            
            summation = sum(['XXX' in x for x in row['Proteins']])
            assert(summation == 0 or summation == len(row['Proteins']))
            if summation == 0:
                return True
            else:
                return False
        else:
            if 'XXX' not in row['Proteins']:
                return True
            else:
                return False
    def _insert_netmhc_ranks(self, output_path):
        """
        self.ranks should be a dictionary that looks like this:

        {'header1': {'targets': {...}, 'decoys':{...}}, 'header2': {'targets': {...}, 'decoys': {...}}}
        
        The headers could something along the lines of "H-2-Kb_rank"

        Output path is the path to write the modified PIN to.
        """


        
        new_fieldnames = self.fieldnames[0:10] + list(self.ranks.keys()) + self.fieldnames[10::]
        with open(output_path, 'w') as g:
            writer = csv.DictWriter(g, delimiter='\t', fieldnames = new_fieldnames)
            writer.writeheader()
            for key in ['targets', 'decoys']:
                row_list = self.target_rows
                if key == 'decoys':
                    row_list = self.decoy_rows
                for row in row_list:
                    if row and row['Proteins']:
                        row_copy = dict(row)
                        assert(isinstance(row['Proteins'], list) or isinstance(row['Proteins'], tuple) or isinstance(row['Proteins'], str))
                        for header, d in self.ranks.items():
                            peptide = PINParser.parse_peptide(row['Peptide'], int(row['PepLen']))
                            if len(peptide) < self.min_peptide_length or len(peptide) > self.max_peptide_length:
                                print('peptide is of wrong size: ' + peptide, file=sys.stderr)
                            if peptide in d[key]:
                                row_copy[header] = d[key][peptide]
                                writer.writerow(row_copy)
                            else:
                                print('Peptide: %s is not in d[key]' % peptide, file=sys.stderr)
                                
                    else:
                        print('bad row or bad proteins: %s', str(row), file=sys.stderr)
                    
class PeptideMatch:
    def __init__(self, peptide, q_value, score):
        self.peptide = peptide
        self.q_value = q_value
        self.score = score
    def get_peptide(self):
        return self.peptide
    def get_q_value(self):
        return self.q_value
    def get_score(self):
        return self.score
    
class SpectrumMatches:
    def __init__(self, scan_number, peptide_matches):
        self.scan_number = scan_number
        self.peptide_matches = peptide_matches

    def get_scan_number(self):
        return self.scan_number
    def get_peptide_matches(self):
        return self.peptide_matches


class MSGFPlusSearchParser:
    def __init__(self, mzid_location):
        print('mzid location: ' + mzid_location)
        tree = ET.parse(mzid_location)
        root = tree.getroot()
        ns = {'mz': 'http://psidev.info/psi/pi/mzIdentML/1.1'}
        peptide_elements = root.findall('./mz:SequenceCollection/mz:Peptide', ns)
        self.peptide_map = {}
        for peptide_element in peptide_elements:
            peptide_id = peptide_element.attrib['id']
            peptide_sequence_element = peptide_element.find('./mz:PeptideSequence', ns)
            peptide = peptide_sequence_element.text
            self.peptide_map[peptide_id] = peptide
        spectrum_identification_results = root.findall('./mz:DataCollection/mz:AnalysisData/mz:SpectrumIdentificationList/mz:SpectrumIdentificationResult', ns)
        self.spectrum_matches = []
        re_matcher = re.compile('index=(?P<index>\d+)')
        
        for result in spectrum_identification_results:
            spectrum_id_string = None
            for param in result.findall('./mz:cvParam', ns):
                if 'name' in param.attrib and param.attrib['name'] == 'scan number(s)':
                    spectrum_id_string = param.attrib['value']
            if spectrum_id_string is None:
                print('Spectrum ID: ' + result.attrib['spectrumID'])
            assert(spectrum_id_string)
            spectrum_identification_items = result.findall('./mz:SpectrumIdentificationItem', ns)
            spectrum_id = int(spectrum_id_string)
            #sometimes there are multiple matches with the same score. For example, SLYDAFKV and SIYDAFPKV have the same mass (It's difficult to differentiate between L and I because they have the same mass).
            peptide_matches = []
            for item in spectrum_identification_items:
                peptide_ref = item.attrib['peptide_ref']
                peptide = self.peptide_map[peptide_ref]
                q_value_item = item.find("./mz:cvParam[@name='MS-GF:QValue']", ns)
                assert(q_value_item is not None)
                q_value = float(q_value_item.attrib['value'])
                score_item = item.find("./mz:cvParam[@name='MS-GF:RawScore']", ns)
                assert(score_item is not None)
                score = float(score_item.attrib['value'])
                peptide_matches.append(PeptideMatch(peptide, q_value, score))
            self.spectrum_matches.append(SpectrumMatches(spectrum_id, peptide_matches))

    def get_spectrum_matches(self):
        return self.spectrum_matches

class CustomizableMQParamParser:
    """
    There shouldn't be any FASTA files or RAW files specified in the mqpar.xml file
    """
    def __init__(self, location):
        self.tree = ET.parse(location)
        self.root = self.tree.getroot()
        fasta_elements = self.root.findall('./fastaFiles')
        for element in fasta_elements:
            self.root.remove(element)
        fixed_combined_elements = self.root.findall('fixedCombinedFolder')
        for element in fixed_combined_elements:
            self.root.remove(element)
        self.output_element = None
        self.fasta_element = None
        peptide_fdr_elements = self.root.findall('peptideFdr')
        for element in peptide_fdr_elements:
            self.root.remove(element)
        self.peptide_fdr_element = None
        file_path_elements = self.root.findall('./filePaths/string')
        for filePath in self.root.findall('filePaths'):
            for string_element in filePath.findall('string'):
                path = string_element.text
                if path.endswith('.raw'):
                    filePath.remove(string_element)
        """
        for path_element in file_path_elements:
            path = path_element.text
            if path.endswith('.raw'):
                self.root.remove(path_element)
        """
        self.raw_element = None
    def set_fasta(self, path):
        self.fasta_element = ET.Element('fastaFiles')
        fasta_info_element = ET.SubElement(self.fasta_element, 'FastaFileInfo')
        elements = [('fastaFilePath', path), ('identifierParseRule', '>(.*)'), ('descriptionParseRule', '>(.*)'), ('taxonomyParseRule', ''), ('variationParseRule', ''), ('modificationParseRule', ''), ('taxonomyId', '')]
        for element_name, text in elements:
            new_element = ET.SubElement(fasta_info_element, element_name)
            new_element.text = text
    def set_raw(self, raw_path):
        self.raw_element = ET.Element('string')
        self.raw_element.text = raw_path
    def set_output_location(self, path):
        self.output_element = ET.Element('fixedCombinedFolder')
        self.output_element.text = path
    def set_peptide_fdr(self, fdr):
        self.peptide_fdr_element = ET.Element('peptideFdr')
        self.peptide_fdr_element.text = str(fdr)
    def write_mq(self, location):
        assert(self.raw_element is not None)
        assert(self.fasta_element is not None)
        assert(self.output_element is not None)
        assert(self.peptide_fdr_element is not None)
        self.root.append(self.fasta_element)
        self.root.append(self.output_element)
        self.root.append(self.peptide_fdr_element)
        file_paths = self.root.find('./filePaths')
        file_paths.append(self.raw_element)
        with open(location, 'w') as f:
            text = ET.tostring(self.tree.getroot(), encoding='unicode')
            print('text')
            print(text)
            f.write(unescape(text))

        #self.tree.write(location)
class MaxQuantPeptidesParser:
    def __init__(self, location):
        self.peptides = set()
        self.num_psms = 0
        with open(location, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                self.peptides.add(row['Sequence'])
                self.num_psms += 1
    def get_peptides(self):
        return self.peptides
    def get_num_psms(self):
        return self.num_psms
        
class MGFScan:
    def __init__(self, start_line, end_line):
        self.start_line = start_line
        self.end_line = end_line
        self.visible = True
    def get_start_line(self):
        return self.start_line
    def get_end_line(self):
        return self.end_line
    def make_visible(self):
        self.visible = True
    def make_invisible(self):
        self.visible = False
    def get_visible(self):
        return self.visible
class MGFParser:
    def __init__(self, location):
        self.location = location
        self.scans = {}
        scan_number_re = re.compile('SCANS=(?P<scan>\d+)')
        with open(location, 'r') as f:
            i = 0
            """
            stage 0 is when we are between an END IONS line (or the begining of the file) and the next START IONS line (or after the last END IONS line)
            stage 1 is when we are between a START IONS line and the corresponding END IONS line
            """
            stage = 0
            start_line = -1
            scan_number = -1
            for line in f:
                if stage == 0:
                    assert(start_line == -1)
                    assert(scan_number == -1)
                    assert('END IONS' not in line)
                    if 'BEGIN IONS' in line:
                        start_line = i
                        stage = 1
                elif stage == 1:
                    assert(start_line >= 0)
                    assert('BEGIN IONS' not in line)
                    if 'END IONS' in line:
                        assert(scan_number > -1)
                        self.scans[scan_number] = MGFScan(start_line, i)
                        start_line = -1
                        scan_number = -1
                        stage = 0
                    elif 'SCANS=' in line:
                        match = scan_number_re.match(line)
                        assert(match)
                        scan_number = int(match.group('scan'))                        
                i += 1

    def remove_scans(self, scan_list):
        """
        Just pass a list of the scan numbers
        """
        for scan_num in set(scan_list):
            mgfscan_object = self.scans[scan_num]
            mgfscan_object.make_invisible()
    def restore_scans(self, scan_list):
        for scan_num in set(scan_list):
            mgfscan_object = self.scans[scan_num]
            mgfscan_object.make_visible()
    def write_modified_mgf(self, location):
        ranges = []
        for key, mgfscan_object in self.scans.items():
            if mgfscan_object.get_visible():
                ranges.append(mgfscan_object)
        ranges.sort(key = lambda x: x.get_start_line())
        line_number = 0
        range_index = 0
        with open(location, 'w') as output_file:
            with open(self.location, 'r') as input_file:
                for line in input_file:
                    while range_index < len(ranges) and line_number > ranges[range_index].get_end_line():
                        range_index = range_index + 1
                        
                    if range_index < len(ranges) and line_number >= ranges[range_index].get_start_line() and line_number <= ranges[range_index].get_end_line():
                        output_file.write(line)
                    line_number += 1
                    
            
