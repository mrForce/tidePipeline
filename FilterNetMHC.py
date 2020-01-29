import Base
import DB
import argparse
import sys
import os

parser = argparse.ArgumentParser(description='Filter a NetMHC Run')

parser.add_argument('project_folder', help='The location of the project folder')


parser.add_argument('rank', help='The rank cutoff', type=float)
parser.add_argument('filtered_name', help='FilteredNetMHC Name')
parser.add_argument('netmhc', help='NetMHC Names', nargs='+')

args = parser.parse_args()
assert(float(args.rank) <= 100.0 and float(args.rank) >= 0.0)
project_folder = args.project_folder
print('project folder: ' + project_folder)
project = Base.Base(project_folder, ' '.join(sys.argv))

netmhc_rows = [project.db_session.query(DB.NetMHC).filter_by(Name = x).first() for x in args.netmhc]
assert(netmhc_rows)
for x in netmhc_rows:
    print('row: ')
    print(x)

project.filter_netmhc(args.rank, args.filtered_name, netmhc_rows)

project.end_command_session()

