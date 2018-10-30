import Base
import argparse
import sys

parser = argparse.ArgumentParser(description='List HLA')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)




args = parser.parse_args()
    

project_folder = args.project_folder[0]


project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
hlas = project.list_hla()

print('ID | HLA ')
for hla in hlas:
    print(hla['id'] + ' | ' + hla['name'])

project.end_command_session()
