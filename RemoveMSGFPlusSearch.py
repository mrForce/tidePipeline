import RowRemoval
import argparse
import sys
import os
import MSGFPlusEngine
parser = argparse.ArgumentParser(description='Remove an MSGF+ search')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('name', help='The name of the MSGF+ search to remove')


args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)



project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))

project.begin_command_session()

row = project.get_msgfplus_search(args.name)
remover = RowRemoval.RowRemoval(project.db_session, row, project_folder)
remover.prompt_user()

project.end_command_session()

