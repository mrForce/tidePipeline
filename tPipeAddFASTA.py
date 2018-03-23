import tPipeDB
import tPipeProject
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Add a FASTA file to the project')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

parser.add_argument('FASTAPath', help='Path to the FASTA file', nargs=1)

parser.add_argument('FASTAName', help='Name of the FASTA file (note that this must be unique)', nargs=1)

parser.add_argument('--FASTAComment', help='Comment about the FASTA file', nargs=1)

args = parser.parse_args()

project_folder = args.project_folder[0]


print('project folder: ' + project_folder)


name = args.FASTAName[0]
comment = ''
if args.FASTAComment:
    comment = args.FASTAComment[0]

project = tPipeProject.Project(project_folder, ' '.join(sys.argv))

project.add_fasta_file(args.FASTAPath[0], name, comment)
project.commit()
#project.commit()
