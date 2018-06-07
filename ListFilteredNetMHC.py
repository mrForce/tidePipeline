import tPipeDB
import Base
import argparse
import sys

parser = argparse.ArgumentParser(description='List FilteredNetMHCs')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)
parser.add_argument('--peptideListName', help='Only list FilteredNetMHCs derived from a certain PeptideList', nargs=1)
parser.add_argument('--hla', help='Only list FilteredNetMHCs scored with a certain HLA allele', nargs=1)
args = parser.parse_args()
project_folder = args.project_folder[0]
project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()


header, results = project.get_list_filtered_netmhc(args.peptideListName, args.hla)
print(' | '.join(header))
for result in results:
    print(' | '.join([result[x] for x in header]))


project.end_command_session()
