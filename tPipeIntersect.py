import re
import argparse
import tPipeProject
import sys
import os
import tPipeDB
from Bio import SeqIO


def extract_peptides_from_fasta(fasta_path, output_path):
    with open(fasta_path, 'rU') as input_handle:
        with open(output_path, 'wU') as output_handle:
            for record in SeqIO.parse(input_handle, 'fasta'):
                sequence = record.seq
                if len(sequence) > 0:
                    output_handle.write(sequence + '\n')
                


union_parse = re.compile('(?P<type>TargetSet|FilteredNetMHC|PeptideList|FilteredSearchResult)\.(?P<name>\S+)(\s+|$)')
parser = argparse.ArgumentParser(description = 'Take the intersection of two collections of peptides (each set may be composed of the union of multiple sets). \n Each set is identified by a string of the form: <type>.<name>, where <type> is either TargetSet, PeptideList or FilteredNetMHC, and <name> is the name of the TargetSet, PeptideList or FilteredNetMHC')
parser.add_argument('project_path', help='The location of the project folder', nargs=1)
parser.add_argument('CollectionOne', help='This is a string that contains at least one set (if there are multiple sets, they should be seperated by whitespace)')
parser.add_argument('CollectionTwo', help='This is a string that contains at least one set (if there are multiple sets, they should be seperated by whitespace)')
parser.add_argument('--output_location', help='This is where we write the peptides that result from the intersection. This is optional; if it is not specified, then the peptides are written to standard out')

args = parser.parse_args()

project_folder = args.project_folder[0]

print('project folder: ' + project_folder)

project = tPipeProject.Project(project_folder, ' '.join(sys.argv))

collection_one = []
collection_two = []

for match in union_parse.finditer(args.CollectionOne):
    set_type = match.group('type')
    set_name = match.group('name')
    collection_one.append((set_type, set_name))
for match in union_parse.finditer(args.CollectionTwo):
    set_type = match.group('type')
    set_name = match.group('name')
    collection_two.append((set_type, set_name))
    
project.begin_command_session()
for set_type, set_name in collection_one + collection_two:
    if set_type == 'FilteredNetMHC':
        if not project.verify_filtered_netMHC(set_name):
            print('There is no FilteredNetMHC entry with the name: ' + set_name)
            project.end_command_session()
            assert(False)
    elif set_type == 'TargetSet':
        if not project.verify_target_set(set_name):
            print('There is no TargetSet entry with the name: ' + set_name)
            project.end_command_session()
            assert(False)
    elif set_type == 'PeptideList':
        if not project.verify_peptide_list(set_name):
            print('There is no PeptideList entry with the name: ' + set_name)
            project.end_command_session()
            assert(False)
    else:
        print('That is not a valid table. The regex should have caught that.')
        project.end_command_session()
        assert(False)

            

    
