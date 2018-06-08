import Base
import argparse
import sys
from Errors import *
parser = argparse.ArgumentParser(description='Initialize tPipe Project. This creates a folder, with a sqlite file in it, and subfolders for FASTA, peptides, NetMHC outputs, Tide Indices, MGF files, Tide search results, and Percolator results')

parser.add_argument('project_folder', help='The location of the project folder')


args = parser.parse_args()

project_folder = args.project_folder

try:
    Base.Base.createEmptyProject(project_folder)
except ProjectPathAlreadyExistsError as e:
    print('A file or directory already exists at that location. Exiting')
    sys.exit()
except Exception as e:
    sys.exit()
