import MSGFPlusEngine
import argparse
import sys

parser = argparse.ArgumentParser(description='List MSGF+ Searches')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('--mgfName', help='List only MSGF+ searches that searched against the given MGF file')
parser.add_argument('--msgfIndexName', help='List only MSGF+ searches that searched against the given MSGF+ index')
args = parser.parse_args()

project_folder = args.project_folder



project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))
project.begin_command_session(False)
searches = project.list_search(mgf_name = args.mgfName, index_name = args.msgfIndexName)
print('id   |   MSGF+ Search Name   | Result path |   MSGF+ Index Name   |   MGF name')
for row in searches:
    print(str(row.idSearch) + ' | ' + row.SearchName + ' | ' + row.resultFilePath + ' | ' + row.index.MSGFPlusIndexName + ' | ' + row.mgf.MGFName)

project.end_command_session(False)
