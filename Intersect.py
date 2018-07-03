import re
import argparse

import PostProcessing
import sys
import os
from Bio import SeqIO
import tempfile
import subprocess


def extract_peptides_from_fasta(fasta_path, output_path):
    with open(fasta_path, 'rU') as input_handle:
        with open(output_path, 'wU') as output_handle:
            for record in SeqIO.parse(input_handle, 'fasta'):
                sequence = record.seq
                if len(sequence) > 0:
                    output_handle.write(sequence + '\n')
                


union_parse = re.compile('(?P<type>TargetSet|FilteredNetMHC|PeptideList|FilteredSearchResult|MaxQuantSearch)\.(?P<name>\S+)(\s+|$)')
parser = argparse.ArgumentParser(description = 'Take the intersection of two collections of peptides (each set may be composed of the union of multiple sets). \n Each set is identified by a string of the form: <type>.<name>, where <type> is either TargetSet, PeptideList, MaxQuantSearch, FilteredSearchResult, or FilteredNetMHC, and <name> is the name of the TargetSet/PeptideList/FilteredSearchResult/FilteredNetMHC/MaxQuantSearch')
parser.add_argument('project_folder', help='The location of the project folder', nargs=1)
parser.add_argument('CollectionOne', help='This is a string that contains at least one set (if there are multiple sets, they should be seperated by whitespace). Multiple sets will be unioned together.')
parser.add_argument('CollectionTwo', help='This is a string that contains at least one set (if there are multiple sets, they should be seperated by whitespace). Multiple sets will be unioned together.')
parser.add_argument('--output_location', help='This is where we write the peptides that result from the intersection. This is optional; if it is not specified, then the peptides are written to standard out')

args = parser.parse_args()

project_folder = args.project_folder[0]

print('project folder: ' + project_folder)

project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))

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
    elif set_type == 'MaxQuantSearch':
        if not project.verify_maxquant_search(set_name):
            print('There is no MaxQuantSearch entry with the name: ' + set_name)
            print.end_command_session()
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
    elif set_type == 'FilteredSearchResult':
        if not project.verify_filtered_search_result(set_name):
            print('There is no FilteredSearchResult entry with the name: ' + set_name)
            project.end_command_session()
            assert(False)
    else:
        print('That is not a valid table. The regex should have caught that.')
        project.end_command_session()
        assert(False)
collection_one_files = []
collection_two_files = []
temp_files = []
def get_path(set_type, set_name):
    file_path = ''
    if set_type == 'FilteredNetMHC':
        file_path = os.path.join(project_folder, project.get_filtered_netmhc_row(set_name).filtered_path)
    elif set_type == 'PeptideList':
        file_path = os.path.join(project_folder, project.get_peptide_list_row(set_name).PeptideListPath)
    elif set_type == 'FilteredSearchResult':
        file_path = os.path.join(project_folder, project.get_filtered_search_result_row(set_name).filteredSearchResultPath)
    elif set_type == 'MaxQuantSearch':
        """FINISH THIS LATER!"""
        f = tempfile.NamedTemporaryFile()
        fasta_file_path = os.path.join(project_folder, project.get_target_set_row(set_name).TargetSetFASTAPath)
        extract_peptides_from_fasta(fasta_file_path, f.name)
        file_path = f.name
        temp_files.append(f)
    elif set_type == 'TargetSet':
        #this is a little more complicated -- need to create a temporary file
        f = tempfile.NamedTemporaryFile()
        fasta_file_path = os.path.join(project_folder, project.get_target_set_row(set_name).TargetSetFASTAPath)
        extract_peptides_from_fasta(fasta_file_path, f.name)
        file_path = f.name
        temp_files.append(f)
    else:
        assert(False)
    return file_path

for set_type, set_name in collection_one:
    collection_one_files.append(get_path(set_type, set_name))
for set_type, set_name in collection_two:
    collection_two_files.append(get_path(set_type, set_name))

t_file = tempfile.NamedTemporaryFile()
temp_files.append(t_file)
collection_one_combined_file = t_file.name
if len(collection_one_files) == 1:
    subprocess.call(['bash_scripts/sort.sh', collection_one_files[0], t_file.name])
else:
    subprocess.call(['bash_scripts/combine_and_uniq_files.sh'] + collection_one_files + [collection_one_combined_file])

t_file = tempfile.NamedTemporaryFile()
temp_files.append(t_file)
collection_two_combined_file = t_file.name
if len(collection_two_files) == 1:
    subprocess.call(['bash_scripts/sort.sh', collection_two_files[0], t_file.name])
else:
    subprocess.call(['bash_scripts/combine_and_uniq_files.sh'] + collection_two_files + [collection_two_combined_file])

if args.output_location and len(args.output_location) > 0:
    subprocess.call(['bash_scripts/peptide_intersection.sh', collection_one_combined_file, collection_two_combined_file, args.output_location])
else:
    subprocess.call(['comm', '-12', collection_one_combined_file, collection_two_combined_file])

project.end_command_session()
