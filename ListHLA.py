import Base
import argparse
import sys

parser = argparse.ArgumentParser(description='List HLA')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

parser.add_argument('--speciesName', help='This is optional, but you can also provide the species name if you only want to list HLAs for that species', nargs=1)

parser.add_argument('--speciesID', help='This is optional, but you can also provide the ID of the species if you want to only list HLAs for that species', nargs=1)



args = parser.parse_args()
    

project_folder = args.project_folder[0]


project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
hlas = []
if args.speciesName:
    hlas = project.list_hla(species_name = args.speciesName[0])
elif args.speciesID:
    hlas = project.list_hla(species_id = args.speciesID[0])
else:
    hlas = project.list_hla()

print('ID | HLA | Species Name | Species ID')
for hla in hlas:
    print(hla['id'] + ' | ' + hla['name'] + ' | ' + hla['species_name'] + ' | ' + hla['species_id'])

project.end_command_session()
