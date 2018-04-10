from abc import ABC, abstractmethod

class Error(Exception):
    pass

class LatexTableRowLengthDifferentFromNumHeadersError(Error):
    def __init__(self, headers, row):
        self.headers = headers
        self.row = row
    def __repr__(self):
        return 'The headers for this Latex Table are: ' + str(self.headers) + ' But the row: ' + str(self.rows) + ' has a different length'

class LatexObject(ABC):
    @abstractmethod
    def getLatexCode(self):
        pass

class LatexTable(LatexObject):
    def __init__(self, headers, rows):
        self.headers = headers
        header_length = len(self.headers)
        self.rows = rows
        for row in rows:
            if len(row) != header_length:
                raise LatexTableRowLengthDifferentFromNumHeadersError(headers, row)
        
    def getLatexCodeLines(self):
        lines = ['\\begin{tabular}{|' + ' l |'*len(self.headers) + '}', '\hline']
        for row in self.rows:
            lines.append(' & '.join(row) + '\\\\ \hline')
        lines.append('\hline')
        lines.append('\end{tabular}')
        return lines

def extract_columns(file_path, column_names):
    

    
class AssignConfidenceHandler:

    """
    This needs to get several things:
    The name of the row
    The MGF name
    The Tide Search Name
    Peptides
    PSMs
    """
    def __init__(self, assign_confidence_row, q_val_column, threshold, project_path):
        self.assign_confidence_name = assign_confidence_row.AssignConfidenceName
        self.mgf_name = assign_confidence_row.tideSearch.mgf.MGFName
        self.tide_search_name = assign_confidence_row.tideSearch.TideSearchName
        self.peptides = set()
        self.psms = set()
        #we need to extract scan, peptide and q value
        
        
    def getName(self):
        return self.assign_confidence_name
    def getMGFName(self):
        return self.mgf_name
    def getTideSearchName(self):
        return self.tide_search_name
class Report:
    """
    For a report, we're only working with AssignConfidence for now.

    Input: a list of tuples of the form (AssignConfidence, threshold). 

    AssignConfidence is a row in the AssignConfidence table
    """
    def __init__(self, assign_confidence_runs):
        self.assign_confidence_runs = assign_confidence_runs
        self.latex_objects = []
        self.images = []


        
