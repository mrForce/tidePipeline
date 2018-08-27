import Base
import PostProcessing
import argparse
import sys
import os

parser = argparse.ArgumentParser(description='Export the peptides from a TargetSet, PeptideList, FilteredSearchResult, TideIterativeSearch, MaxQuantSearch, or FilteredNetMHC')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('CollectionType', help='Is this a TargetSet, PeptideList, FilteredSearchResult, Tide Iterative Search, MaxQuantSearch or FilteredNetMHC?', choices=['TargetSet', 'PeptideList', 'FilteredSearchResult', 'FilteredNetMHC', 'MaxQuantSearch', 'TideIterativeSearch', 'MSGFPlusIterativeSearch'])
parser.add_argument('Name', help='The name of the TargetSet, PeptideList FilteredSearchResult, TideIterativeSearch, MaxQuantSearch or FilteredNetMHC to export')

parser.add_argument('export_location', help='File to put the peptides')

parser.add_argument('--overwrite', help='By default, this script doesn\'t overwrite files. Set this to True if you want to overwrite the output', type=bool, default=False)
parser.add_argument('--contaminants', help='If this is of type FilteredSearchResult, by default, we do not export the contaminants. If you supply this option with a filepath, it will write the contaminant peptides in the FilteredSearchResult to the filepath')




args = parser.parse_args()

project_folder = args.project_folder



assert((not os.path.isdir(args.export_location)) or (os.path.commonpath([os.path.abspath(args.export_location), os.devnull]) == os.devnull))


assert(args.overwrite or (not os.path.isfile(args.export_location)))
if args.contaminants:
    assert((not os.path.isdir(args.contaminants)) or (os.path.commonpath([os.path.abspath(args.contaminants), os.devnull]) == os.devnull))
    assert(args.overwrite or (not os.path.isfile(args.contaminants)))
    try:
        with open(args.contaminants, 'w') as f:
            pass
    except:
        assert(False)


try:
    with open(args.export_location, 'w') as f:
        pass
except:
    assert(False)


project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
project.begin_command_session()
row = None
if args.CollectionType == 'FilteredSearchResult' or args.CollectionType == 'TideIterativeSearch' or args.collectionType == 'MSGFPlusIterativeSearch':
    print('in')
    if args.CollectionType == 'FilteredSearchResult':
        row = project.get_filtered_search_result_row(args.Name)
    elif args.CollectionType == 'TideIterativeSearch':
        row = project.get_tideiterativerun_row(args.Name)
    else:
        row = project.get_msgfplusiterativesearch_row(args.Name)
    contaminant_sets = row.get_contaminant_sets()
    print('contaminant sets')
    print(contaminant_sets)
    contaminant_peptides = set()
    if contaminant_sets:
        for contaminant_set in contaminant_sets:
            peptide_file = os.path.join(project.project_path, contaminant_set.peptide_file)
            with open(peptide_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if len(line) > 1:
                        contaminant_peptides.add(line)
    peptides = row.get_peptides(project_folder)
    contaminant_file = None
    if args.contaminants:
        contaminant_file = open(args.contaminants, 'w')
    with open(args.export_location, 'w') as f:
        for peptide in list(peptides):
            if peptide not in contaminant_peptides:
                f.write(peptide + '\n')
            elif contaminant_file:
                contaminant_file.write(peptide + '\n')
    if contaminant_file:
        contaminant_file.close()
    print('contaminant peptides')
    print(contaminant_peptides)
else:
    if args.CollectionType == 'TargetSet':
        row = project.get_target_set_row(args.Name)
    elif args.CollectionType == 'PeptideList':
        row = project.get_peptide_list_row(args.Name)
    elif args.CollectionType == 'FilteredNetMHC':
        row = project.get_filtered_netmhc_row(args.Name)
    elif args.CollectionType == 'MaxQuantSearch':
        row = project.get_maxquant_search_row(args.Name)
    assert(row)
    peptides = row.get_peptides(project_folder)
    with open(args.export_location, 'w') as f:
        for peptide in list(peptides):
            f.write(peptide + '\n')
            
project.end_command_session()
