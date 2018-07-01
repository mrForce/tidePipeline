import xml.etree.ElementTree as ET
import re
import csv
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
            spectrum_identification_items = result.findall('./mz:SpectrumIdentificationItem', ns)
            spectrum_id_string = result.attrib['spectrumID']
            spectrum_id = int(re_matcher.match(spectrum_id_string).group('index'))
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
        self.tree.write(location)
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
        

