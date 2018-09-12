import Base
import argparse
import sys
parser = argparse.ArgumentParser(description='Import a PeptideList')
parser.add_argument('project_folder')
parser.add_argument('location', help='Location of the NetMHC output')
parser.add_argument('HLA', help='Name of the HLA')
parser.add_argument('PeptideListName', help='The peptide list that NetMHC was ran on')
parser.add_argument('--rankCutoff', action='append')

args = parser.parse_args()
project_folder = args.project_folder
location = args.location
hla = args.HLA
peptide_list_name = args.PeptideListName
project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
if 'rankCutoff' in args:
    project.import_netmhc_run(hla, location, peptide_list_name, args.rankCutoff)
else:
    project.import_netmhc_run(hla, location, peptide_list_name)
project.end_command_session()
