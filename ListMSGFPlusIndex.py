import MSGFPlusEngine
import argparse
import sys
import pprint
parser = argparse.ArgumentParser(description='List MSGF+ indices')

parser.add_argument('project_folder', help='The location of the project folder')


args = parser.parse_args()
    

project_folder = args.project_folder



project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))
project.begin_command_session()
indices = project.list_indices()
printer = pprint.PrettyPrinter(indent=3)
print('indices')
printer.pprint(indices)
project.end_command_session()
