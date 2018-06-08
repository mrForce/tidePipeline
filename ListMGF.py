import Base
import argparse
import sys

parser = argparse.ArgumentParser(description='List MGF files')

parser.add_argument('project_folder', help='The location of the project folder')


args = parser.parse_args()
    

project_folder = args.project_folder



project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
print('ID | MGF name | path')
for t in project.list_mgf_db():
    print(str(t['id']) + ' | ' + t['name'] + ' | ' +  t['path'])
project.end_command_session()
