import tPipeDB
import tPipeProject
import argparse
import sys

parser = argparse.ArgumentParser(description='List Species')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

parser.add_argument('--showHLA', help='Use this flag if you want to show the HLA types for each species', action='store_true')


args = parser.parse_args()
    

project_folder = args.project_folder[0]



project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
print('ID | Species Name')
for t in project.get_species():
    print(str(t['id']) + ' | ' + t['name'])
    if args.showHLA:
        for hla in t['hla']:
            print('\t' + hla)
        
project.commit()
