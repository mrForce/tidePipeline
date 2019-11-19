import subprocess
import os
import collections
import tempfile
from Errors import *
from Bio import SeqIO
import shutil
import random

def shuffle_string(string):
    l = list(string)
    random.shuffle(l)
    return ''.join(string)


"""
This function uses awk, and ensures that there's a newline between each file.
"""
def concat_files_with_newline(input_paths, output_path):
    command = ['awk', '1'] + input_paths
    with open(output_path, 'w') as f:
        proc = subprocess.Popen(command, stdout=f)
        try:
            outs, errors = proc.communicate()
        except:
            raise AWKFailedError(command)
        if proc.returncode != 0:
            raise NonZeroReturnCodeError(command, proc.returncode)
    
def call_target_netmhc_rank(peptides_location, output_location_ranked, output_location_affinity, parsed_netmhc_runs):
    if output_location_affinity == None:
        output_location_affinity = '/dev/null'
    print('peptides location: ' + peptides_location)

    print('output location ranked: '+ output_location_ranked)
    print('output location affinity: ' + output_location_affinity)
    command = ['bash_scripts/target_netmhc_rank.sh', peptides_location, output_location_ranked, output_location_affinity] + list(parsed_netmhc_runs)
    proc = subprocess.Popen(command)
    try:
        print('about to communicate')
        outs,errors = proc.communicate()
        print('communicated')
    except:
        assert(False)
    if proc.returncode != 0:
        raise NonZeroReturnCodeError(command, proc.returncode)

class ParsedNetMHC:
    #row is a row from the NetMHC table
    def __init__(self, project_location, row):
        self.location = os.path.join(project_location, row.PeptideRankPath)
        self.length = row.length()
        self.row = row
    def get_row(self):
        return self.row
    def get_location(self):
        return self.location
    def get_length(self):
        return self.length

def extract_peptides_with_length(location, length):
    #peptides can be in FASTA or peptide format. Returns the output location (hint: it's a temporary file)
    print('command: ' + ' '.join(['bash_scripts/extract_peptides_with_length.sh', location, length]))
    command = ['bash_scripts/extract_peptides_with_length.sh', location, length]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    try:
        outs, errors = proc.communicate()
    except:
        assert(False)
    if proc.returncode != 0:
        raise NonZeroReturnCodeError(command, proc.returncode)
    output_location = outs.strip().decode('utf-8')
    assert(os.path.isfile(output_location))
    return output_location
def num_lines(file_path):
    print('command: ' + ' '.join(['grep', '-c', '-v', '^ *$', file_path]))
    command = ['grep', '-c', '-v', '^ *$', file_path]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    try:
        outs, errors = proc.communicate()
    except:
        assert(False)
    if proc.returncode != 0:
        raise NonZeroReturnCodeError(command, proc.returncode)
    output = outs.strip().decode('utf-8')
    return int(output.split(' ')[0])


def merge_netmhc_runs(mode, netmhc_runs):
    #netmhc_runs is a list of filenames. This returns the output location, which is a temp file created by mktemp
    print('command: ' + ' '.join(['bash_scripts/merge_netmhc_runs.sh', mode] +  netmhc_runs))
    command = ['bash_scripts/merge_netmhc_runs.sh', mode] +  netmhc_runs
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    try:
        outs, errors = proc.communicate()
    except:
        assert(False)
    if proc.returncode != 0:
        raise NonZeroReturnCodeError(command, proc.returncode)
    output_location = outs.strip().decode('utf-8')
    assert(os.path.isfile(output_location))
    return output_location

def call_netmhc_decoys(input_location, target, num_decoys):
    #returns the output location (which is a temporary file)
    print('command: ' + ' '.join(['bash_scripts/netmhc_decoys.sh', input_location, target, str(num_decoys)]))
    command = ['bash_scripts/netmhc_decoys.sh', input_location, target, str(num_decoys)]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    try:
        outs, errors = proc.communicate()
    except:
        assert(False)
    if proc.returncode != 0:
        raise NonZeroReturnCodeError(command, proc.returncode)
    output_location = outs.strip().decode('utf-8')
    print('output location')
    print(output_location)
    assert(os.path.isfile(output_location))
    return output_location

def call_merge_and_sort(files):
    #files should be a list of file paths
    print(os.getcwd())
    print('command: ' + ' '.join(['bash_scripts/merge_and_sort.sh'] + files))
    command = ['bash_scripts/merge_and_sort.sh'] + files
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    try:
        outs, errors = proc.communicate()
    except:
        assert(False)
    if proc.returncode != 0:
        raise NonZeroReturnCodeError(command, proc.returncode)
    output_location = outs.strip().decode('utf-8')
    assert(os.path.isfile(output_location))
    return output_location

def join_peptides_to_fasta(input_locations, output_location, prefix=None):
    if isinstance(input_locations, str):
        input_locations = [input_locations]
    #prefix is what goes between the > and line number in the FASTA headers
    if prefix:
        print('command : ' + ' '.join(['bash_scripts/join_peptides_to_fasta.sh', '-P', prefix] +  input_locations + [output_location]))
        command = ['bash_scripts/join_peptides_to_fasta.sh', '-P', prefix] +  input_locations + [output_location]
        rc = subprocess.call(command)
        if rc != 0:
            raise NonZeroReturnCodeError(command, rc)
    else:
        print('command: ' + ' '.join(['bash_scripts/join_peptides_to_fasta.sh'] + input_locations + [output_location]))
        command = ['bash_scripts/join_peptides_to_fasta.sh'] + input_locations + [output_location]
        rc = subprocess.call(command)
        if rc != 0:
            raise NonZeroReturnCodeError(command, rc)

def generateDecoys(target_location, output_location, decoy_type, decoy_prefix = '>XXX_'):
    #decoy_prefix is what is used to seperate decoys from targets in the FASTA file
    random.seed()
    shutil.copyfile(target_location, output_location)
    print('target location: ' + target_location)
    print('output location: ' + output_location)
    with open(output_location, 'a') as f:
        for record in SeqIO.parse(target_location, 'fasta'):
            fasta_header = record.description
            f.write(decoy_prefix + str(fasta_header) + '\n')
            peptide = str(record.seq).strip()
            if len(peptide) == 0:
                print('peptide zero length!')
                assert(False)
            shuffled_line = ''
            if decoy_type == 'random':
                shuffled_line = shuffle_string(peptide)
            elif decoy_type == 'tide_random':
                shuffled_line = peptide[0] + shuffle_string(peptide[1:-1]) + peptide[-1]
            elif decoy_type == 'reverse':
                shuffled_line = peptide[::-1]
            elif decoy_type == 'tide_reverse':
                shuffled_line = peptide[0] + peptide[1:-1][::-1] + peptide[-1]
            f.write(shuffled_line + '\n')

            


            
"""
parsed_netmhc_objects must be a list of ParsedNetMHC instances

"""
def netMHCDecoys(parsed_netmhc_objects, target_location, output_location, *, merge_mode = 0, decoy_prefix = '>XXX_'):
    print('hello')
    merged_decoy_candidates = call_merge_and_sort([x[1] for x in parsed_netmhc_objects.items()])

    num_target_lines = num_lines(target_location)
    print('target location')
    print(target_location)
    decoy_location = call_netmhc_decoys(merged_decoy_candidates, target_location, str(int(num_target_lines/2)))
    print('decoy location')
    print(decoy_location)
    with tempfile.NamedTemporaryFile() as f:
        with open(decoy_location, 'r') as g:
            for record in SeqIO.parse(target_location, 'fasta'):
                fasta_header = record.description
                f.write(str(decoy_prefix).encode() + str(fasta_header).encode() + b'\n')
                peptide = g.readline().strip()
                if len(peptide) == 0:
                    print('peptide zero length!')
                    input('waiting')
                assert(len(peptide) > 0)
                f.write(peptide.encode() + b'\n')
        os.remove(decoy_location)
        combine_files([output_location, f.name], output_location)
    
   
    
    

def line_length_set(location):
    """
    This  automatically removes any FASTA headers
    """
    print('command: ' + ' '.join(['bash_scripts/line_length_set.sh', location]))
    command = ['bash_scripts/line_length_set.sh', location]
    proc = subprocess.Popen(command, stdout = subprocess.PIPE)
    try:
        outs, errs = proc.communicate()
    except:
        assert(False)
    print(outs)
    if proc.returncode != 0:
        raise NonZeroReturnCodeError(command, proc.returncode)
    return set([int(x) for x in outs.split()])

def extract_netmhc_output(input_location, output_location):
    assert(os.path.isfile(input_location))
    print('command: ' + ' '.join(['awk', '-f', 'bash_scripts/extract_netmhc_ic50.awk', input_location, output_location]))
    command = ['awk', '-f', 'bash_scripts/extract_netmhc_ic50.awk', input_location, output_location]
    rc = subprocess.call(command)
    if rc != 0:
        raise NonZeroReturnCodeError(command, rc)
    

def netmhc_percentile(input_location, output_location):
    assert(os.path.isfile(input_location))
    print('command: ' + ' '.join(['bash_scripts/netmhc_percentile.sh', input_location, output_location]))
    command = ['bash_scripts/netmhc_percentile.sh', input_location, output_location]
    rc = subprocess.call(command)
    if rc != 0:
        raise NonZeroReturnCodeError(command, rc)

def combine_files(input_files, output_file):
    #print('combine files: ' + ' '.join(['bash_scripts/combine_files.sh', *input_files, output_file]))
    command = ['bash_scripts/combine_files.sh'] + list(input_files)+  [output_file]
    rc = subprocess.call(command)
    if rc != 0:
        raise NonZeroReturnCodeError(command, rc)


def top_percent_netmhc(input_location, percent, output_location):
    assert(os.path.isfile(input_location))
    assert(float(percent) > 0.0)
    assert(float(percent) <= 100.0)
    print('command: ' + ' '.join(['bash_scripts/top_percent.sh', os.path.abspath(input_location), str(percent), os.path.abspath(output_location)]))
    command = ['bash_scripts/top_percent.sh', os.path.abspath(input_location), str(percent), os.path.abspath(output_location)]
    rc = subprocess.call(command)
    if rc != 0:
        raise NonZeroReturnCodeError(command, rc)
    assert(os.path.isfile(output_location))
