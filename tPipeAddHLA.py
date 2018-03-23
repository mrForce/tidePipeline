import tPipeDB
import tPipeProject
import argparse
import sys

parser = argparse.ArgumentParser(description='Add an HLA to the tPipe project')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

parser.add_argument('HLA', help='Name of the HLA')

parser.add_argument('species', help='By default, this is the name of the species. If you use the --speciesID flag, it is the database ID of the species', nargs=1)

parser.add_argument('--speciesID', help='If this flag is present, then species will be interpreted as the ID of the row for the species', action='store_true')

args = parser.parse_args()

project_folder = args.project_folder[0]


print('project folder: ' + project_folder)
species = args.species[0]


print('species: ' + species)
print('hla: ' + args.HLA)
print('speciesID: ' + str(args.speciesID))
print('not doing anything')
project = tPipeProject.Project(project_folder, ' '.join(sys.argv))

project.add_hla(args.HLA, species, args.speciesID)
#project.commit()
