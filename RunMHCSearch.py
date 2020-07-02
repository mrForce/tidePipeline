import Base
import argparse
import sys
import threading
import os
import csv
import re
import itertools
import DB
import Runners
import MSGFPlusEngine
import PostProcessing

concurrent_searches = 7

parser = argparse.ArgumentParser(description='We have a collection of MGF files. For each one, we want to perform two searches: Against an unfiltered proteome, and against a proteome filtered by NetMHC score (we take the top k percent of scorers for each allele-length combination. This is different from the Rank included in the NetMHC output). Then, we run percolator three times: against the unfiltered search, against the filtered search, and against the unfiltered search but with NetMHC score inserted into the PIN file for the peptide. Note that when there are multiple alleles, we take the best NetMHC score for the peptide. The information about the MGF files is stored in a TSV file. We will have one index for the unfiltered searches. However, we will create an index for each MGF file when doing filtered.')
parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('TSVPath', help='TSV Location')

parser.add_argument('MGFDirectory', help='Directory containing the MGF files')

parser.add_argument('Index', help='Unfiltered index to search against')

parser.add_argument('fragmentation', type=int, choices=[0, 1, 2], help='0: CID, 1: ETD, 2: HCD')
parser.add_argument('instrument', type=int, choices=[0, 1, 2, 3], help='0: Low-res LCQ/LTQ, 1: High-res LTQ, 2: TOF, 3: Q-Exactive')


parser.add_argument('MGFColumn', help='Need the row that contains the MGF names.')
parser.add_argument('--allelesColumn', help='The column containing the alleles that will be passed to NetMHC. They should be seperated by commas')
parser.add_argument('--rank_cutoff', help='The rank cutoff to use when creating the filtered index. Percent, so 2 is top two percent.', type=float)

parser.add_argument('--memory', help='The amount of memory to give the jar file when searching. Default is 3500 megabytes', type=int)
parser.add_argument('--modifications_name', help='Name of the modifications file to use. Optional')

parser.add_argument('--min_length', type=int, help='min peptide length', default=8)
parser.add_argument('--max_length', type=int, help='max peptide length', default=12)


parser.add_argument('--percolator_param_file', help='Parameter file for percolator')
parser.add_argument('--num_matches_per_spectrum', type=int, help='Number of matches per spectrum', default=1)


"""
Naming of stuff. 

Unfiltered search: <mgf_name>_unfiltered_search
Unfiltered percolator: <mgf_name>_unfiltered_search_percolator
Unfiltered percolator with NetMHC scores: <mgf_name>_unfiltered_search_netmhc_percolator

Filtered index: <mgf_name>_filtered_index
Filtered search: <mgf_name>_filtered_index_search
Filtered percolator: <mgf_name>_filtered_index_search_percolator
"""


args = parser.parse_args()


search_arguments = {}

min_length = args.min_length
max_length = args.max_length
rank = args.rank_cutoff


assert(rank >= 0.0 and rank <= 100.0)
if args.min_length:
    search_arguments['minLength'] = args.min_length

if args.max_length:
    search_arguments['maxLength'] = args.max_length

    

project_folder = args.project_folder


print('project folder: ' + project_folder)
tsv_path = args.TSVPath
mgf_directory = args.MGFDirectory

unfiltered_index = args.Index

"""
For unfiltered search, use unspecific cleavage, aka enzyme 0. It actually shouldn't matter here.

For filtered search, use enzyme is 8. 1 is added to the enzyme to create the EnzymeID given to MS-GF+. 
"""


fragmentation = args.fragmentation

instrument = args.instrument

mgf_column = args.MGFColumn

alleles_column = args.allelesColumn

filtered_search = False
if alleles_column and rank:
    filtered_search = True

data = []
headers = None
with open(tsv_path, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    headers = [x.strip() for x in reader.fieldnames]
    for x in reader:
        data.append({k.strip(): v.strip() for k,v in x.items()})

print('headers')
print(headers)
for row in data:
    assert(mgf_column in row)
    assert(len(row[mgf_column].strip()) > 0)
    mgf_location = os.path.join(mgf_directory, row[mgf_column].strip() + '.mgf')
    print('MGF location: ' + mgf_location)    
    assert(os.path.isfile(mgf_location))


project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()

def get_netmhc_name(length, allele):
    return 'Proteome' + str(length) + 'Mers_' + allele
def get_filtered_name(length, allele, rank):
    return 'Proteome' + str(length) + 'Mers_' + allele + '_' + str(rank) + '_filtered'

print('checking NetMHC present')
netmhc_names = {}
for row in data:
    alleles = row[alleles_column].split(',')
    for allele in alleles:
        for length in range(min_length, max_length + 1):
            netmhc_name = get_netmhc_name(length, allele)
            if netmhc_name not in netmhc_names:
                print('checking for NetMHC: ' + netmhc_name)
                assert(project.db_session.query(DB.NetMHC).filter_by(Name = netmhc_name).first())
                netmhc_names[netmhc_name] = get_filtered_name(length, allele, rank)

print('adding MGF files')
for row in data:
    mgf_name = row[mgf_column].strip()
    if project.verify_row_existence(DB.MGFfile.MGFName, mgf_name):
        print('mgf already imported: ' + mgf_name)
    else:
        mgf_location = os.path.join(mgf_directory, mgf_name + '.mgf')
        print('Adding mgf file: ' + mgf_location)
        #8 is the enzyme; no cleavage. This gets overridden when we run the unfiltered search, because the index comes from a FASTA.
        project.add_mgf_file(mgf_location, mgf_name, 8, fragmentation, instrument)

print('added MGF files')
if filtered_search:
    print('Going to filter NetMHC.')
    for netmhc_name, filtered_netmhc_name in netmhc_names.items():
        print('NetMHC name: ' + netmhc_name + ', filtered name: ' + filtered_netmhc_name)
        if project.verify_row_existence(DB.FilteredNetMHC.FilteredNetMHCName, filtered_netmhc_name):
            print('skipping filtered netmhc: ' + filtered_netmhc_name)
        else:
            project.filter_netmhc(rank, filtered_netmhc_name, [project.db_session.query(DB.NetMHC).filter_by(Name = netmhc_name).first()])
            assert(project.verify_row_existence(DB.FilteredNetMHC.FilteredNetMHCName, filtered_netmhc_name))
    print('filtered NetMHC')
    project.end_command_session()
    project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))
    project.begin_command_session()
    print('going to create TargetSet and index for each MGF file.')
    
    mgf_to_targetset = {}
    mgf_to_filtered_index = {}
    msgfplus_index_runner = Runners.MSGFPlusIndexRunner(project.get_msgfplus_executable_path())
    for row in data:
        mgf_name = row[mgf_column].strip()
        alleles = row[alleles_column].split(',')
        filtered_netmhc_names = []
        for allele in alleles:
            for length in range(min_length, max_length + 1):
                filtered_netmhc_names.append(get_filtered_name(length, allele, rank))
        targetset_name = mgf_name + '_filtered_targetset'
        index_name = mgf_name + '_filtered_index'
        print('going to create targetset: ' + targetset_name)
        print('filtered netmhc names: ' + ', '.join(filtered_netmhc_names))
        if project.verify_target_set(targetset_name):
            print('skipping targetset: ' + targetset_name + ' it already exists')
        else:
            project.add_targetset(filtered_netmhc_names, [], targetset_name)
            assert(project.verify_target_set(targetset_name))
        mgf_to_targetset[mgf_name] = targetset_name
        print('going to create index: ' + index_name)
        if project.verify_row_existence(DB.MSGFPlusIndex.MSGFPlusIndexName, index_name):
            print('skipping index: ' + index_name + ' it already exists')
        else:
            if args.memory:
                project.create_index('TargetSet', targetset_name, msgfplus_index_runner, index_name, [], args.memory)
            else:
                project.create_index('TargetSet', targetset_name, msgfplus_index_runner, index_name)
            assert(project.verify_row_existence(DB.MSGFPlusIndex.MSGFPlusIndexName, index_name))
            
    print('created filtered indices')


    project.end_command_session()






print('Going to run searches')


msgfplus_jar = project.executables['msgfplus']

modifications_name = None
if args.modifications_name:
    modifications_name = args.modifications_name


#semaphore is used to limit the number of concurrent searches.
search_semaphore = threading.Semaphore(concurrent_searches)
if __name__ == '__main__':
    threads_and_rows = []
    project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))
    project.begin_command_session()
    for row in data:
        unfiltered_search_runner = Runners.MSGFPlusSearchRunner(search_arguments, msgfplus_jar, semaphore = search_semaphore)
        rows = []
        thread = None
        mgf_name = row[mgf_column]
        search_name = mgf_name + '_unfiltered_search'
        if args.memory:
            rows, thread = project.run_search(mgf_name, unfiltered_index, modifications_name, unfiltered_search_runner, search_name, args.memory, threaded=True)
        else:
            rows, thread = project.run_search(mgf_name, unfiltered_index, modifications_name, unfiltered_search_runner, search_name, threaded = True)
        assert(rows)
        assert(thread)
        threads_and_rows.append((rows, thread))
        if filtered_search:
            filtered_search_runner = Runners.MSGFPlusSearchRunner({}, msgfplus_jar, semaphore = search_semaphore)
            search_name = mgf_name + '_filtered_index_search'
            index_name = mgf_name + '_filtered_index'
            if args.memory:
                rows, thread = project.run_search(mgf_name, index_name, modifications_name, filtered_search_runner, search_name, args.memory, threaded=True)
            else:
                rows, thread = project.run_search(mgf_name, index_name, modifications_name, filtered_search_runner, search_name, threaded=True)
            assert(rows)
            assert(thread)
            threads_and_rows.append((rows, thread))
        
    for rows, thread in threads_and_rows:
        thread.start()
    for rows, thread in threads_and_rows:
        thread.join()
        for row in rows:
            project.db_session.add(row)
        project.db_session.commit()
    project.end_command_session()

print('Going to run percolator')

project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
crux_exec_path = project.get_crux_executable_path()
project.begin_command_session()

percolator_runner = None

if args.percolator_param_file:
    project.verify_row_existence(DB.PercolatorParameterFile.Name, args.percolator_param_file)
    param_file_row = project.get_percolator_parameter_file(args.percolator_param_file)
    percolator_runner = Runners.PercolatorRunner(crux_exec_path, project.project_path, param_file_row)
else:
    percolator_runner = Runners.PercolatorRunner(crux_exec_path, project.project_path)


    
for row in data:
    mgf_name = row[mgf_column]
    unfiltered_search_name = mgf_name + '_unfiltered_search'
    percolator_name = unfiltered_search_name + '_percolator'
    print('going to run percolator: ' + percolator_name)
    print(project)
    project.percolator(unfiltered_search_name, 'msgfplus', percolator_runner, percolator_name, num_matches_per_spectrum = args.num_matches_per_spectrum)
    if args.percolator_param_file:
        percolator_runner = Runners.PercolatorRunner(crux_exec_path, project.project_path, param_file_row)
    else:
        percolator_runner = Runners.PercolatorRunner(crux_exec_path, project.project_path)
    percolator_name = unfiltered_search_name + '_netmhc_percolator'
    print('going to run percolator: ' + percolator_name)
    if alleles_column:
        project.percolator(unfiltered_search_name, 'msgfplus', percolator_runner, percolator_name, num_matches_per_spectrum = args.num_matches_per_spectrum, alleles = row[alleles_column].split(','))

    if filtered_search:
        filtered_search_name = mgf_name + '_filtered_index_search'
        percolator_name = filtered_search_name + '_percolator'
        print('going to run percolator: ' + percolator_name)
        if args.percolator_param_file:
            percolator_runner = Runners.PercolatorRunner(crux_exec_path, project.project_path, param_file_row)
        else:
            percolator_runner = Runners.PercolatorRunner(crux_exec_path, project.project_path)
        project.percolator(filtered_search_name, 'msgfplus', percolator_runner, percolator_name, num_matches_per_spectrum = args.num_matches_per_spectrum)
    
    
    
project.end_command_session()

