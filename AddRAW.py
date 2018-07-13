import Base
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Add a RAW file to the project')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('RAWPath', help='The location of the RAW file')

parser.add_argument('RAWName', help='Name of the RAW file (this must be unique')


args = parser.parse_args()

project_folder = args.project_folder


print('project folder: ' + project_folder)


name = args.RAWName
path = args.RAWPath 

project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
project.add_raw_file(path, name)
project.end_command_session()

