import Base
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Add an MS-GF+ Modifications file to the project')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

parser.add_argument('Name', help='Name of the modifications file')

parser.add_argument('location', help='Location of the modifications file')



args = parser.parse_args()

project_folder = args.project_folder[0]


print('project folder: ' + project_folder)


name = args.Name
path = args.location
assert(os.path.isfile(path))

project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
project.add_msgfplus_mod_file(name, path)
project.end_command_session()

