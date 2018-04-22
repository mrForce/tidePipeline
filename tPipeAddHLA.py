import tPipeDB
import tPipeProject
import argparse
import sys

parser = argparse.ArgumentParser(description='Add an HLA to the tPipe project')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

parser.add_argument('HLA', help='Name of the HLA')


args = parser.parse_args()

project_folder = args.project_folder[0]


print('project folder: ' + project_folder)



print('hla: ' + args.HLA)

print('not doing anything')
project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
project.begin_command_session()
project.add_hla(args.HLA)
project.end_command_session()
