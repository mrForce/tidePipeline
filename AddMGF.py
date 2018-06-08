import Base
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Add an MGF file to the project')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('MGFPath', help='The location of the MGF file')

parser.add_argument('MGFName', help='Name of the MGF file (this must be unique')


args = parser.parse_args()

project_folder = args.project_folder


print('project folder: ' + project_folder)


name = args.MGFName
path = args.MGFPath

project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
project.add_mgf_file(path, name)
project.end_command_session()

