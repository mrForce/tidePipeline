import RowRemoval
import argparse
import sys
import os
import Base
import DB
parser = argparse.ArgumentParser(description='Remove a NetMHC')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('name', help='The name of NetMHC')
parser.add_argument('--all', action='store_true', default=False)

args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)



project = Base.Base(project_folder, ' '.join(sys.argv))

project.begin_command_session()
if args.all:
    for row in project.db_session.query(DB.NetMHC).all():
        remover = RowRemoval.RowRemoval(project.db_session, row, project_folder)
        remover.prompt_user()
else:
    row = project.get_netmhc_row(args.name)
    remover = RowRemoval.RowRemoval(project.db_session, row, project_folder)
    remover.prompt_user()

project.end_command_session()

