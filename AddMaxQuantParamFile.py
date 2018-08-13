import Base
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Add a MaxQuant parameter file to the project')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('Path', help='The location of the MaxQuant Parameter file')

parser.add_argument('Name', help='Name of the MaxQuant Parameter file (this must be unique)')

parser.add_argument('--comment', help='A comment about the parameter file (optional)')
args = parser.parse_args()

project_folder = args.project_folder


print('project folder: ' + project_folder)


name = args.Name
path = args.Path
if args.comment is None:
    comment = ''
else:
    comment = args.comment

project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
project.add_maxquant_parameter_file(path, name, comment)
project.end_command_session()

