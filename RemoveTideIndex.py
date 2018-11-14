import RowRemoval
import argparse
import sys
import os
import TideEngine
parser = argparse.ArgumentParser(description='Remove a Tide index')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('name', help='The name of the Tide index')

args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)



project = TideEngine.TideEngine(project_folder, ' '.join(sys.argv))

project.begin_command_session()

row = project.get_tide_index(args.name)
remover = RowRemoval.RowRemoval(project.db_session, row, project_folder)
remover.prompt_user()

project.end_command_session()

