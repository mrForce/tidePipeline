import Base
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Join two or more FASTA files to make a new FASTA file')

parser.add_argument('project_folder', help='The location of the project folder', type=str)

parser.add_argument('FASTAName', help='Name of the resultant FASTA file', type=str)

parser.add_argument('InputFASTAs', help='List of FASTA files to join', nargs=argparse.REMAINDER)

parser.add_argument('--FASTAComment', help='Comment about the FASTA file', type=str)

args = parser.parse_args()

assert(len(args.InputFASTAs) >= 2)

project_folder = args.project_folder


print('project folder: ' + project_folder)


name = args.FASTAName
comment = ''
if args.FASTAComment:
    comment = args.FASTAComment[0]

project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
project.concat_fasta_files(name, args.InputFASTAs, comment)
project.end_command_session()

