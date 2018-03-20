import tPipeDB
import tPipeProject
import argparse
import sys

parser = argparse.ArgumentParser(description='Initialize tPipe Project. This creates a folder, with a sqlite file in it, and subfolders for FASTA, peptides, NetMHC outputs, Tide Indices, MGF files, Tide search results, and Percolator results')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

args = parser.parse_args()

project_folder = args.project_folder[0]

try:
    tPipeProject.Project.createEmptyProject(project_folder)
except tPipeProject.ProjectPathAlreadyExistsError as e:
    print('A file or directory already exists at that location. Exiting')
    sys.exit()
except Exception as e:
    sys.exit()
