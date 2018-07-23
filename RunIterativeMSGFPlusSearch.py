import TideEngine
import PostProcessing
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Run an iterative MSGF+ search')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('mgf_name', help='The name of the MGF ')
parser.add_argument('fdr', type=float, help='False Discovery Rate')
parser.add_argument('iterativesearch_name', help='Name of the iterative search')
parser.add_argument('msgfplusindices', nargs='+', help='At least 2 MSGF+ indexes to do the searches against. Will do it in the order specified.')
parser.add_argument('--modifications_name', help='Name of the modifications file to use. Optional')
parser.add_argument('--memory', help='The amount of memory to give the jar file. Default is 3500 megabytes', type=int)
for k, v in Runners.MSGFPlusSearchRunner.get_search_options().items():
    parser.add_argument(k, **v)

project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))
msgfplus_jar = project.executables['msgfplus']
good_arguments = {}

arguments = vars(args)


for k, v in arguments.items():
    if k and v and k != 'project_folder' and k != 'mgf_name' and k != 'msgfplusindices' and k != 'iterativesearch_name' and k != 'modifications_file' and k != 'memory' and k != 'fdr':
        k = k.replace('_', '-')
        good_arguments[k] = v
postprocessing_object = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))


arguments = vars(args)
print('going to begin command session')        
project.begin_command_session()
project.multistep_search(args.mgf_name, args.msgfplusindices, good_arguments, args.iterativesearch_name, args.fdr, postprocessing_object, args.modifications_name, args.memory)
project.end_command_session()

