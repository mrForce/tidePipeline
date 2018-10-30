import TideEngine
import argparse
import sys

parser = argparse.ArgumentParser(description='List Tide Searches')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('--mgfName', help='List only tide-searches that searched against the given MGF file')
parser.add_argument('--tideIndexName', help='List only tide-searches that searched against the given tide index')
parser.add_argument('--showIterative', help='By default, this doesn\'t show tide searches that were part of iterative searches. Using this option, it will show tide searches that were part of iterative searches.', action='store_true')
args = parser.parse_args()

project_folder = args.project_folder



project = TideEngine.TideEngine(project_folder, ' '.join(sys.argv))
project.begin_command_session(False)
tide_searches = project.list_search(mgf_name = args.mgfName, tide_index_name = args.tideIndexName)
print('id   |   Tide Search Name   |   Tide Index Name   |   MGF name   |   target path')
for row in tide_searches:
    if (args.showIterative and row.partOfIterativeSearch) or (not row.partOfIterativeSearch):
        print(str(row.idSearch) + '   |   ' + row.SearchName + '   |   ' + row.tideindex.TideIndexName + '   |   ' + row.mgf.MGFName + '   |   ' + row.targetPath)
project.end_command_session(False)
