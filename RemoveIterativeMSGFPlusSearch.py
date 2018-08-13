import RowRemoval
import argparse
import sys
import os
import PostProcessing
parser = argparse.ArgumentParser(description='Run an iterative MSGF+ Search')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('name', help='The name of the iterative MSGF+ Search')


args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)



project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))

project.begin_command_session()
row = project.get_msgfplusiterativesearch_row(args.name)
remover = RowRemoval.RowRemoval(project.session, row, project_folder)
message = remover.get_deletion_message()
print(message)
while True:
    response = input('Do you want to make the changes show above? (y/n)')
    if response == 'y':
        break
    elif response == 'n':
        sys.exit(0)
remover.delete()
project.end_command_session()

