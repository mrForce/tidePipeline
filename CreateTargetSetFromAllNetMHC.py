import Base

import argparse
import DB
import sys
import os
parser = argparse.ArgumentParser(description='Create a TargetSet from all of the FilteredNetMHCs in the project (I mainly added this for use in Galaxy)')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('TargetSetName', help='Name of the TargetSet')

args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)
project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()

header, results = project.get_list_filtered_netmhc()

filtered_netmhc = []
for x in results:
    print('result')
    print(x)
    filtered_netmhc.append(x['ID'])

project.add_targetset(filtered_netmhc, [], args.TargetSetName)

project.end_command_session()
