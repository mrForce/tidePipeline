import TideEngine
import PostProcessing
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Run an iterative tide search')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('mgf_name', help='The name of the MGF ')
parser.add_argument('fdr', type=float, help='False Discovery Rate')
parser.add_argument('peptide_identifier', choices=['percolator', 'assign-confidence'])
parser.add_argument('iterativesearch_name', help='Name of the iterative search')
parser.add_argument('tideindices', nargs='+', help='At least 2 tide indexes to do the searches against. Will do it in the order specified.')
parser.add_argument('--peptide_identifier_param_file', help='Path to a param file for percolator or assign-confidence (depending on which one you are using)')
parser.add_argument('--tidesearch_param_file')

args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)



project = TideEngine.TideEngine(project_folder, ' '.join(sys.argv))
postprocessing_object = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
crux_exec_path = project.get_crux_executable_path()
arguments = vars(args)
print('going to begin command session')        
project.begin_command_session()
project.multistep_search(args.mgf_name, args.tideindices, args.tidesearch_param_file, args.iterativesearch_name, args.fdr, args.peptide_identifier, args.peptide_identifier_param_file, postprocessing_object)
project.end_command_session()

