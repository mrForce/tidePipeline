import tPipeDB
import TideSearchProject
import argparse
import sys
import pprint
parser = argparse.ArgumentParser(description='List Tide indices')

parser.add_argument('project_folder', help='The location of the project folder')


args = parser.parse_args()
    

project_folder = args.project_folder



project = TideSearchProject.TideSearchProject(project_folder, ' '.join(sys.argv))
project.begin_command_session()
indices = project.get_tide_indices()
printer = pprint.PrettyPrinter(indent=3)
print('indices')
printer.pprint(indices)
project.end_command_session()
