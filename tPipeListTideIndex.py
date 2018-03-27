import tPipeDB
import tPipeProject
import argparse
import sys

parser = argparse.ArgumentParser(description='List Tide indices')

parser.add_argument('project_folder', help='The location of the project folder')


args = parser.parse_args()
    

project_folder = args.project_folder



project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
project.begin_command_session()
indices = project.get_tide_indices()
print('indices')
print(indices)
project.end_command_session()