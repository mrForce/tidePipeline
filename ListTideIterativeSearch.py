import TideEngine
import argparse
import sys

parser = argparse.ArgumentParser(description='List iterative Tide Searches')

parser.add_argument('project_folder', help='The location of the project folder')


args = parser.parse_args()

project_folder = args.project_folder



project = TideEngine.TideEngine(project_folder, ' '.join(sys.argv))
project.begin_command_session(False)
searches = project.list_multistep_search()
print('id   |   Iterative Search Name   |   FDR   |   MGF name   | Peptide Identifier | Num steps ')
for row in searches:
    print(str(row.idTideIterativeRun) + '   |   ' + row.TideIterativeRunName + '   |   ' + row.fdr + '   |   ' + row.mgf.MGFName + '   |   ' + row.PeptideIdentifierName + '    |    '  + str(row.num_steps))
project.end_command_session(False)
