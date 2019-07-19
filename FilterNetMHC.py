import Base
import DB
import argparse
import sys
import os

parser = argparse.ArgumentParser(description='Filter a NetMHC Run')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('netmhc', help='NetMHC Name')

parser.add_argument('rank', help='The rank cutoff', type=float)
parser.add_argument('filtered_name', help='FilteredNetMHC Name')

args = parser.parse_args()
assert(float(args.rank) <= 100.0 and float(args.rank) >= 0.0)
project_folder = args.project_folder
print('project folder: ' + project_folder)
project = Base.Base(project_folder, ' '.join(sys.argv))

netmhc_row = project.db_session.query(DB.NetMHC).filter_by(Name = args.netmhc).first()
assert(netmhc_row)
project.filter_netmhc(args.rank, args.filtered_name, netmhc_row)

project.end_command_session()

