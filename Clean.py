import Base
import argparse
import sys
import os
import DB
import MSGFPlusEngine
import TideEngine
parser = argparse.ArgumentParser(description='Clean out invalid things')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

args = parser.parse_args()
project_folder = args.project_folder[0]
print('project folder: ' + project_folder)
tide_project = TideEngine.TideEngine(project_folder, ' '.join(sys.argv))
tide_project.begin_command_session(False)
searches = tide_project.list_search()
for search in searches:
    print('search')
    print(search)
    print('Checking tide search: ' + search.identifier())
    if search.is_valid():
       print('search is valid')
    else:
        print('search is not valid')
        tide_project.delete_row(search)
tide_project.end_command_session(False)

msgf_project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))
msgf_project.begin_command_session(False)
searches = msgf_project.list_search()
for search in searches:
    print('Checking MSGF+ search: ' + search.identifier())
    if search.is_valid():
       print('search is valid')
    else:
        print('search is not valid')
        msgf_project.delete_row(search)
mgf_files = msgf_project.db_session.query(DB.MGFfile).all()
for row in mgf_files:
    print('Checking MGF file: ' + str(row))
    if row.is_valid():
        print('MGF file is valid')
    else:
        print('MGF file is not valid')
        msgf_project.delete_row(row)
msgf_project.end_command_session(False)


