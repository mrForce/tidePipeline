import tPipeDB
import tPipeProject
import argparse
import sys

parser = argparse.ArgumentParser(description='List Peptide Lists')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)
args = parser.parse_args()
project_folder = args.project_folder[0]
project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
project.begin_command_session()
print('ID | Peptide List Name | FASTA Name | FASTA Path | Length | Peptide List File Path')
for x in project.list_peptide_lists():
    print(str(x['id']) + ' | ' + x['name'] + ' | ' + x['FASTAName'] + ' | ' + x['FASTAPath'] + ' | '+ str(x['length']) + ' | ' + x['path'])
project.end_command_session()
