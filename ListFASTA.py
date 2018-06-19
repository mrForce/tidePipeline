import Base
import argparse
import sys

parser = argparse.ArgumentParser(description='List FASTA files')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

parser.add_argument('--showPeptideLists', help='Use this flag if you want to show the peptide lists associated with each FASTA file', action='store_true')


args = parser.parse_args()
    

project_folder = args.project_folder[0]



project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
print('ID | FASTA name | Comment | path')
for t in project.list_fasta_db():
    print(str(t['id']) + ' | ' + t['name'] + ' | ' + t['comment'] + ' | ' + t['path'])
    if args.showPeptideLists and len(t['peptide_lists']) > 0:
        print('\tpeptide list name | length')
        for x in t['peptide_lists']:
            print('\t' + x['name'] + ' | ' + str(x['length']))        
project.end_command_session()
