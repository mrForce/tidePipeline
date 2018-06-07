from abc import ABC, abstractmethod
import subprocess
import tempfile
import os
import locale
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
    #column_names should be a list
    encoding = locale.getpreferredencoding()
    columns_temp_file = tempfile.NamedTemporaryFile(mode='w+t', encoding=encoding)
    command = ['crux extract-columns ' + file_path + ' "' + ','.join(column_names) + '" > ' + columns_temp_file.name]
    print('command: ' + ' '.join(command))
    subprocess.call(command, shell=True)
    rows = []
    columns_temp_file.seek(0)
    for line in columns_temp_file:
        rows.append(line.split())
    columns_temp_file.close()
    #first row are the headers
    return rows[1::]
    
        

class AbstractQValueHandler(ABC):
    @abstractmethod
    def __init__(self, name, q_val_threshold, project_path, db_session):
        pass
    @abstractmethod
    def get_peptides(self):
        """
        Returns a list of peptides from PSMs that met the Q-value threshold
        """
        pass
    @abstractmethod
    def get_psms(self):
        """
        Returns a list of tuples of the form: [(scan, peptide)]. 
        """
        pass
    @abstractmethod
    def get_row(self):
        pass

    
class AssignConfidenceHandler(AbstractQValueHandler):

    """
    This needs to get several things:
    The name of the row
    The MGF name
    The Tide Search Name
    Peptides
    PSMs
    """
    def __init__(self, name, threshold, project_path, db_session):
        self.assign_confidence_row = db_session.query(tPipeDB.AssignConfidence).filter_by(AssignConfidenceName = name).first()
        self.peptides = set()
        self.psms = set()
        #we need to extract scan, peptide and q value
        rows = extract_columns(os.path.join(project_path, self.assign_confidence_row.AssignConfidenceOutputPath, 'assign-confidence.target.txt'), ['scan', 'sequence', 'tdc q-value'])
        for row in rows:
            scan = int(row[0])
            peptide = row[1]
            q_val = float(row[2])
            if q_val <= threshold:
                self.peptides.add(peptide)
                self.psms.add((scan, peptide))
        

    def get_peptides(self):
        return self.peptides
    def get_psms(self):
        return self.psms
    def get_row(self):
        return self.assign_confidence_row
class PercolatorHandler(AbstractQValueHandler):

    """
    This needs to get several things:
    The name of the row
    The MGF name
    The Tide Search Name
    Peptides
    PSMs
    """
    def __init__(self, name, threshold, project_path, db_session):
        self.percolator_row = tPipeDB.query(tPipeDB.Percolator).filter_by(PercolatorName = name).first()
        self.peptides = set()
        self.psms = set()
        #we need to extract scan, peptide and q value
        rows = extract_columns(os.path.join(project_path, self.percolator_row.PercolatorOutputPath, 'percolator.target.psms.txt'), ['scan', 'sequence', 'percolator q-value'])
        for row in rows:
            scan = int(row[0])
            peptide = row[1]
            q_val = float(row[2])
            if q_val <= threshold:
                self.peptides.add(peptide)
                self.psms.add((scan, peptide))
        
    def get_peptides(self):
        return self.peptides
    def get_psms(self):
        return self.psms
    def get_row(self):
        return self.percolator_row
class Report:
    """
    For a report, we're only working with AssignConfidence for now.

    Input: a list of tuples of the form (AssignConfidence, threshold). 

    AssignConfidence is a row in the AssignConfidence table
    """
    def __init__(self, assign_confidence_runs, project_path):
        self.latex_objects = []
        #self.images = []
        self.assign_confidence_handlers = []
        summary_table_headers = ['Assign Confidence Name', 'MGF Name', 'Tide Search Name', 'Total PSMs', '# PSMs Meeting Threshold', '# unique peptides']
        summary_rows = []
        for row, threshold in  assign_confidence_runs:
            q_val_col = row.estimation_method + ' q-value'
            handler = AssignConfidenceHandler(row, q_val_col, threshold, project_path)
            self.assign_confidence_handlers.append(handler)
            summary_rows.append(row.AssignConfidenceName, row.tideSearch.mgf.MGFName, row.tideSearch.TideSearchName, str(handler.getNumPSMs()), str(handler.getNumPassingPSMs()), str(len(handler.getPeptides())))
        self.latex_objects.append(LatexTable(summary_table_headers, summary_rows))
        num_assign_confidence_runs = len(assign_confidence_runs)
        peptide_overlap_headers = ['Assign Confidence Name'] + ['']*(num_assign_confidence_runs - 1) + ['Peptide Overlap']
        peptide_overlap_rows = []
        for num_overlapping_sets in range(2, len(assign_confidence_runs) + 1):
            for run_indices in itertools.combinations(list(range(0, len(assign_confidence_runs))), num_overlapping_sets):                
                sets = [self.assign_confidence_handlers[run_index].getPeptides() for run_index in run_indices]
                names = [self.assign_confidence_handlers[run_index].getName() for run_index in run_indices]
                overlap = len(set.intersection(*sets))
                peptide_overlap_rows.append(names + ['']*(num_assign_confidence_runs - len(names)) + [str(overlap)])
        self.latex_objects.append(LatexTable(peptide_overlap_headers, peptide_overlap_rows))
    def save_report(self, output_location):
        with open(output_location, 'w') as f:
            f.write('\documentclass{article}\n')
            f.write('\\begin{document}\n')
            for latex_object in self.latex_objects:
                for line in latex_object.getLatexCodeLines():
                    f.write(line + '\n')

            f.write('\\end{document}')

        
