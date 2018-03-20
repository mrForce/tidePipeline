import tPipeDB
import tPipeProject
import argparse
import sys

parser = argparse.ArgumentParser(description='Add a species to the tPipe project')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

parser.add_argument('species', help='The name of the species', nargs=1)

args = parser.parse_args()

project_folder = args.project_folder[0]

print('project folder: ' + project_folder)
species = args.species[0]

print('species: ' + species)
project = tPipeProject.Project(project_folder, ' '.join(sys.argv))

project.add_species(species)
project.commit()
