import xml.etree.ElementTree as ET
import re
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
