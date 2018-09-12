import subprocess
import os
import collections
import tempfile
class ParsedNetMHC:
    #row is a row from the NetMHC table
    def __init__(self, project_location, row):
        self.location = os.path.join(project_location, row.PeptideRankPath)
        self.length = row.length()
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

def call_netmhc_decoys(input_location, targets):
    #returns the output location (which is a temporary file)
    proc = subprocess.Popen(['bash_scripts/netmhc_decoys.sh', input_location, targets], stdout=subprocess.PIPE)
    try:
        outs, errors = proc.communicate(timeout=600)
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
    lengths = line_length_set(target_location)
    netmhc_length_dict = collections.defaultdict(list)
    for x in parsed_netmhc_objects:
        netmhc_length_dict[x.get_length()] = x.get_location()
    temp_outputs = []
    for length, locations in netmhc_length_dict.items():
        """
        If there are multple locations, merge the runs using merge_netmhc_runs.sh

        Then, extract the targets with the given length

        Then, call netmhc_decoys.sh
        """
        if len(locations) > 1:
            locations = [merge_netmhc_runs(merge_mode, locations)]
        targets_with_length = extract_peptides_with_length(target_location, length)
        temp_output_location = call_netmhc_decoys(locations[0], targets_with_length)
        temp_outputs.append(temp_output_location)
    with tempfile.NamedTemporaryFile() as f:
        join_peptides_to_fasta(temp_outputs, f.name, 'XXX_')
        for temp_output in temp_outputs:
            os.remove(temp_output)
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
