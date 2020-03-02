import Base

import argparse
import sys
import os
import DB

parser = argparse.ArgumentParser(description='This looks at all the HLA alleles, and runs NetMHC on the peptide list for any alleles that do not already have a NetMHC run for that peptide list')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('peptideList', help='Name of the peptidelist to run NetMHC on')


args = parser.parse_args()

project_folder = args.project_folder
print('project folder: ' + project_folder)
project = Base.Base(project_folder, ' '.join(sys.argv))

netmhc_name = args.peptideList + '_' + args.HLA

project.begin_command_session()

if not project.verify_peptide_list(args.peptideList):
    print('peptide list: ' + args.peptideList + ' does not exist')
    sys.exit()

peptide_list_row = project.db_session.query(DB.PeptideList).filter_by(peptideListName = args.peptideList).first()
    
print(args.peptideList)
query = project.db_session.query(DB.HLA)
rows = query.all()
#hold {'hla': hla, 'netmhc_name': netmhc_name} in here
netmhc_runs_to_make = []
for hla in rows:
    query = project.db_session.query(DB.NetMHC).filter(DB.NetMHC.idHLA == hla.idHLA, DB.NetMHC.peptidelistID == peptide_list_row.idPeptideList)
    netmhc_rows = query.all()
    if len(netmhc_rows) == 0:
        print('Need to call NetMHC on ' + hla.HLAName)
        netmhc_name = args.peptideList + '_' + hla.HLAName
        netmhc_runs_to_make.append({'hla': hla.HLAName, 'netmhc_name': netmhc_name})
    else:
        assert(len(netmhc_rows) < 2)
    
for netmhc_run in netmhc_runs_to_make:
    print('going to call netmhc for: ' + netmhc_run['hla'])
    project.run_netmhc(args.peptideList, netmhc_run['hla'], None, netmhc_run['netmhc_name'], False, False)

project.end_command_session()

