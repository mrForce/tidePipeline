import PostProcessing
import Runners
import argparse
import sys
import os
import DB
parser = argparse.ArgumentParser(description='Run percolator')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('search_type', help='What search engine was used?', choices=['tide', 'msgfplus'])

parser.add_argument('search_name', help='The name of the search to percolator on')

parser.add_argument('percolator_name', help='The name of the percolator run')
parser.add_argument('--param_file', help='Parameter file for percolator')
parser.add_argument('--num_matches_per_spectrum', type=int, help='Number of matches per spectrum')
parser.add_argument('--allele', help='NetMHC allele to use. If you have multiple alleles, the best score for the peptide will be inserted into the PIN', nargs='*')

args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)
assert(args.num_matches_per_spectrum > 0)

project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
crux_exec_path = project.get_crux_executable_path()
arguments = vars(args)
project.begin_command_session()
percolator_runner = None

project.verify_search(args.search_type, args.search_name)


if args.param_file:
    project.verify_row_existence(DB.PercolatorParameterFile.Name, args.param_file)
    row = project.get_percolator_parameter_file(args.param_file)
    percolator_runner = Runners.PercolatorRunner(crux_exec_path, project.project_path, row)
else:
    percolator_runner = Runners.PercolatorRunner(crux_exec_path, project.project_path)
percolator_name = args.percolator_name
project.percolator(args.search_name, args.search_type, percolator_runner, percolator_name, num_matches_per_spectrum = args.num_matches_per_spectrum, alleles=args.allele)
project.end_command_session()

