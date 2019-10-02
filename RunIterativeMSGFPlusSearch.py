import TideEngine
import PostProcessing
import MSGFPlusEngine
import argparse
import Runners
from Errors import *
import sys
import os
import DB
parser = argparse.ArgumentParser(description='Run an iterative MSGF+ search')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('mgf_name', help='The name of the MGF ')
parser.add_argument('fdr', type=float, help='False Discovery Rate')
parser.add_argument('iterativesearch_name', help='Name of the iterative search')
parser.add_argument('msgfplusindices', nargs='+', help='At least 2 MSGF+ indexes to do the searches against. Will do it in the order specified.')
parser.add_argument('--use_percolator', help='If you want to use percolator with MSGF+, you need to provide the name of a Percolator parameter file.')
parser.add_argument('--modifications_name', help='Name of the modifications file to use. Optional')
parser.add_argument('--memory', help='The amount of memory to give the jar file. Default is 3500 megabytes', type=int)
parser.add_argument('--disableContaminantSetCheck', default=False, action='store_true', help='By default, before running the iterative search, we check that each index is attached to the same ContaminantSets. If you include this option, we will not perform this step')
for k, v in Runners.MSGFPlusSearchRunner.get_search_options().items():
    parser.add_argument(k, **v)
args = parser.parse_args()

project_folder = args.project_folder
print('project folder: ' + project_folder)


project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))
if args.use_percolator:
    if not project.verify_row_existence(DB.PercolatorParameterFile.Name, args.use_percolator):
        raise NoSuchPercolatorParameterFileError(args.use_percolator)
msgfplus_jar = project.executables['msgfplus']
good_arguments = {}

arguments = vars(args)


for k, v in arguments.items():
    if k and v and k != 'project_folder' and k != 'mgf_name' and k != 'msgfplusindices' and k != 'iterativesearch_name' and k != 'modifications_file' and k != 'memory' and k != 'fdr' and k != 'use_percolator':
        k = k.replace('_', '-')
        good_arguments[k] = v




print('going to begin command session')        
project.begin_command_session()
postprocessing_object = PostProcessing.PostProcessing(None, None, project)
if args.use_percolator:
    project.multistep_search(args.mgf_name, args.msgfplusindices, good_arguments, args.iterativesearch_name, args.fdr, postprocessing_object, args.use_percolator, args.modifications_name, args.memory, disable_contaminants_check = args.disableContaminantSetCheck)
else:
    project.multistep_search(args.mgf_name, args.msgfplusindices, good_arguments, args.iterativesearch_name, args.fdr, postprocessing_object, False, args.modifications_name, args.memory, disable_contaminants_check = args.disableContaminantSetCheck)
project.end_command_session()

