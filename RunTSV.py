import Base
import argparse
import sys
import os
import csv
import re
import itertools
import DB
import Runners
import MSGFPlusEngine
import PostProcessing

parser = argparse.ArgumentParser(description='Run the pipeline. Use a TSV to specify which MGF files to run, and meta information associated with them. This will import the MGF files into the project, search them against an index, and run Percolator.')
parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('TSVPath', help='TSV Location')

parser.add_argument('MGFDirectory', help='Directory containing the MGF files')

parser.add_argument('Index', help='Index to search against')

parser.add_argument('enzyme', type=int, choices=[0, 1, 2, 3, 4, 5, 6, 7, 8], help='What enzyme was used to generate the data? See ScoringParamGen for options')

parser.add_argument('fragmentation', type=int, choices=[0, 1, 2], help='CID, 1: ETD, 2: HCD')
parser.add_argument('instrument', type=int, choices=[0, 1, 2, 3], help='0: Low-res LCQ/LTQ, 1: High-res LTQ, 2: TOF, 3: Q-Exactive')

parser.add_argument('--MGFColumn', nargs=4, action='append', help='Need four things: A column that contains MGF file names, the format string for the MGF name, format string for search name, and format string for percolator name')

parser.add_argument('--memory', help='The amount of memory to give the jar file when searching. Default is 3500 megabytes', type=int)
parser.add_argument('--modifications_name', help='Name of the modifications file to use. Optional')

parser.add_argument('--percolator_param_file', help='Parameter file for percolator')
parser.add_argument('--num_matches_per_spectrum', type=int, help='Number of matches per spectrum')

args = parser.parse_args()

project_folder = args.project_folder


print('project folder: ' + project_folder)
tsv_path = args.TSVPath
mgf_directory = args.MGFDirectory

index = args.Index

enzyme = args.enzyme

fragmentation = args.fragmentation

instrument = args.instrument

mgf_columns = args.MGFColumn

data = []
headers = None
with open(tsv_path, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    headers = [x.strip() for x in reader.fieldnames]
    for x in reader:
        data.append({k.strip(): v.strip() for k,v in x.items()})

class MGFRow:
    def __init__(self, column, mgf_name_format_string, search_format_string, percolator_format_string, row):
        self.column = column
        assert(column in row)
        self.mgf_file = row[column]
        self.mgf_name = MGFRow.substitute(mgf_name_format_string, row)
        self.search_name = MGFRow.substitute(search_format_string, row)
        self.percolator_name = MGFRow.substitute(percolator_format_string, row)

    def get_column(self):
        return self.column
    def get_mgf_name(self):
        return self.mgf_name
    def get_mgf_file(self):
        return self.mgf_file
    def get_search_name(self):
        return self.search_name
    def get_percolator_name(self):
        return self.percolator_name
    @staticmethod
    def extract_format_string_fields(format_string):
        pattern = '\\{([^\\}\\{]+)\\}'
        fields = re.findall(pattern, format_string)
        return fields
    @staticmethod
    def substitute(format_string, row):
        fields = MGFRow.extract_format_string_fields(format_string)
        print('row')
        print(row)
        for x in fields:
            print('field: ' + x)
            assert(x in row)
        name = format_string
        for x in fields:
            name = name.replace('{' + x + '}', row[x].replace(' ', '_'))
        assert('{' not in name)
        assert('}' not in name)
        return name
    
def fill_missing(format_strings, rows, fields, mgf_columns):
    """
    I intended for the spreadsheet to be hierarchical. Basically, it boils down to this rule: If a cell is blank, and it is used in a format string, then all cells to the left must be blank. If the cell is blank, you can then simply go up the rows until you find that the column is filled in. 
    """
    format_fields = set(itertools.chain.from_iterable([MGFRow.extract_format_string_fields(x) for x in format_strings]))
    data = []
    for i in range(0, len(rows)):
        row = rows[i]
        filled_row = dict(row)
        left_blank = True
        for field in fields:
            if field in format_fields and field not in mgf_columns:
                if len(row[field].strip()) == 0:
                    assert(left_blank)
                    for j in range(1, i + 1):
                        if len(rows[i - j][field].strip()) > 0:
                            filled_row[field] = rows[i - j][field].strip()
                            break
                    assert(len(filled_row[field].strip()) > 0)
                else:
                    left_blank = False
        data.append(filled_row)
    return data

print('headers')
print(headers)
for x in mgf_columns:
    column = x[0]
    print('column: ' + column)
    assert(column in headers)
    for row in data:
        if column in row and len(row[column].strip()) > 0:
            print('MGF location: ' + os.path.join(mgf_directory, row[column].strip() + '.mgf'))
            assert(os.path.isfile(os.path.join(mgf_directory, row[column].strip() + '.mgf')))
filled_rows = fill_missing(list(itertools.chain.from_iterable([x[1::] for x in mgf_columns])), data, headers, [x[0] for x in mgf_columns])

mgf_rows = []
for x in mgf_columns:
    column = x[0]
    mgf_name_format = x[1]
    search_name_format = x[2]
    percolator_name_format = x[3]
    for row in filled_rows:
        if column in row and len(row[column].strip()) > 0:
            mgf_row = MGFRow(column, mgf_name_format, search_name_format, percolator_name_format, row)
            mgf_rows.append(mgf_row)

project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()

print('adding MGF files')
for row in mgf_rows:
    print('Adding mgf file: ' + row.get_mgf_file() + '.mgf')
    path = os.path.join(mgf_directory, row.get_mgf_file() + '.mgf')
    print('mgf path: ' + row.get_mgf_file())
    name = row.get_mgf_name()
    project.add_mgf_file(path, name, enzyme, fragmentation, instrument)
print('added MGF files')
        


project.end_command_session()

print('Going to run searches')

project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))
project.begin_command_session()
msgfplus_jar = project.executables['msgfplus']
search_runner = Runners.MSGFPlusSearchRunner({}, msgfplus_jar)

modifications_name = None
if args.modifications_name:
    modifications_name = args.modifications_name

for row in mgf_rows:
    print('runing search: ' + row.get_search_name())
    if args.memory:
        project.run_search(row.get_mgf_name(), index, modifications_name, search_runner, row.get_search_name(), args.memory)
    else:
        project.run_search(row.get_mgf_name(), index, modifications_name, search_runner, row.get_search_name())

project.end_command_session()
print('Going to run percolator')

project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
crux_exec_path = project.get_crux_executable_path()
project.begin_command_session()

percolator_runner = None

for row in mgf_rows:
    project.verify_search('msgfplus', row.get_search_name())

if args.percolator_param_file:
    project.verify_row_existence(DB.PercolatorParameterFile.Name, args.percolator_param_file)
    param_file_row = project.get_percolator_parameter_file(args.percolator_param_file)
    percolator_runner = Runners.PercolatorRunner(crux_exec_path, project.project_path, param_file_row)
else:
    percolator_runner = Runners.PercolatorRunner(crux_exec_path, project.project_path)

for row in mgf_rows:
    percolator_name = row.get_percolator_name()
    print('going to run percolator: ' + percolator_name)
    project.percolator(row.get_search_name(), 'msgfplus', percolator_runner, percolator_name, num_matches_per_spectrum = args.num_matches_per_spectrum)
    
project.end_command_session()

