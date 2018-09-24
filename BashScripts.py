import subprocess
import os
import collections
import tempfile
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
    proc = subprocess.Popen(['bash_scripts/extract_peptides_with_length.sh', location, length], stdout=subprocess.PIPE)
    try:
        outs, errors = proc.communicate(timeout=240)
    except:
        assert(False)
    output_location = outs.strip()
    assert(os.path.isfile(output_location))
    return output_location
def num_lines(file_path):
    proc = subprocess.Popen(['grep', '-c', '-v', '^ *$', file_path], stdout=subprocess.PIPE)
    try:
        outs, errors = proc.communicate(timeout=240)
    except:
        assert(False)
    output = outs.strip().decode('utf-8')
    return int(output.split(' ')[0])


def merge_netmhc_runs(mode, netmhc_runs):
    #netmhc_runs is a list of filenames. This returns the output location, which is a temp file created by mktemp
    proc = subprocess.Popen(['bash_scripts/merge_netmhc_runs.sh', mode, *netmhc_runs], stdout=subprocess.PIPE)
    try:
        outs, errors = proc.communicate(timeout=240)
    except:
        assert(False)
    output_location = outs.strip()
    assert(os.path.isfile(output_location))
    return output_location

def call_netmhc_decoys(input_location, target, num_decoys):
    #returns the output location (which is a temporary file)
    proc = subprocess.Popen(['bash_scripts/netmhc_decoys.sh', input_location, target, str(num_decoys)], stdout=subprocess.PIPE)
    try:
        outs, errors = proc.communicate(timeout=600)
    except:
        assert(False)
    output_location = outs.strip()
    assert(os.path.isfile(output_location))
    return output_location

def call_merge_and_sort(files):
    #files should be a list of file paths
    proc = subprocess.Popen(['bash_scripts/merge_and_sort.sh', *files], stdout=subprocess.PIPE)
    try:
        outs, errors = proc.communicate(timeout=240)
    except:
        assert(False)
    output_location = outs.strip()
    assert(os.path.isfile(output_location))
    return output_location

def join_peptides_to_fasta(input_locations, output_location, prefix=None):
    #prefix is what goes between the > and line number in the FASTA headers
    if prefix:
        subprocess.call(['bash_scripts/join_peptides_to_fasta.sh', '-P', prefix, *input_locations, output_location])
    else:
        subprocess.call(['bash_scripts/join_peptides_to_fasta.sh', *input_locations, output_location])
"""
parsed_netmhc_objects must be a list of ParsedNetMHC instances

Finish these later
"""
def netMHCDecoys(parsed_netmhc_objects, target_location, output_location, *, merge_mode = 0):
    merged_decoy_candidates = call_merge_and_sort([x[1] for x in parsed_netmhc_objects.items()])
    num_target_lines = num_lines(target_location)
    decoy_location = call_netmhc_decoys(merged_decoy_candidates, target_location, num_target_lines)

    with tempfile.NamedTemporaryFile() as f:
        join_peptides_to_fasta(decoy_location, f.name, 'XXX_')
        os.remove(decoy_location)
        combine_files([output_location, f.name], output_location)
    
   
    
    

def line_length_set(location):
    """
    This  automatically removes any FASTA headers
    """
    proc = subprocess.Popen(['bash_scripts/line_length_set.sh', location], stdout = subprocess.PIPE)
    try:
        outs, errs = proc.communicate(timeout=240)
    except:
        assert(False)
    print(outs)
    return set([int(x) for x in outs.split()])

def extract_netmhc_output(input_location, output_location):
    assert(os.path.isfile(input_location))
    subprocess.call(['awk', '-f', 'bash_scripts/extract_netmhc_ic50.awk', input_location, output_location])

def netmhc_percentile(input_location, output_location):
    assert(os.path.isfile(input_location))
    subprocess.call(['bash_scripts/netmhc_percentile.sh', input_location, output_location])

def combine_files(input_files, output_file):
    subprocess.call(['bash_scripts/combine_files', *input_files, output_file])


def top_percent_netmhc(input_location, percent, output_location):
    assert(os.path.isfile(input_location))
    assert(float(percent) > 0.0)
    assert(float(percent) <= 100.0)
    subprocess.call(['bash_scripts/top_percent.sh', os.path.abspath(input_location), str(percent), os.path.abspath(output_location)])
    assert(os.path.isfile(output_location))
