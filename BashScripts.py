import subprocess
import os
import collections
class ParsedNetMHC:
    #row is a row from the NetMHC table
    def __init__(self, project_location, row):
        self.location = os.path.join(project_location, row.PeptideRankPath)
        self.length = row.length()
    def get_location(self):
        return self.location
    def get_length(self):
        return self.length

"""
parsed_netmhc_objects must be a list of ParsedNetMHC instances

Finish these later
"""
def netMHCDecoys(parsed_netmhc_objects, target_location, output_location):
    lengths = line_length_set(target_location)
    netmhc_length_dict = defaultdict(list)
    for x in parsed_netmhc_objects:
        netmhc_length_dict[x.get_length()] = x.get_location()
    #for length, locations:
        
    assert(subprocess.call(['bash_scripts', 'netmhc_decoys.sh', parsed_netmhc_output_location, target_set_peptides_location, output_location]) == 0)
    

def line_length_set(location):
    """
    This  automatically removes any FASTA headers
    """
    proc = subprocess.Popen(['bash_scripts/line_length_set.sh', location], stdout = subprocess.PIPE)
    try:
        outs, errs = proc.communicate(timeout=60)
    except:
        assert(False)
    print(outs)
    return set([int(x) for x in outs.split()])

def extract_netmhc_output(input_location, output_location):
    assert(os.path.isfile(input_location))
    subprocess.call(['awk', '-f', 'bash_scripts/extract_netmhc_ic50.awk', input_location, output_location])

def netmhc_percentile(input_location, output_location):
    assert(os.path.isfile(input_location))
    subprocess.call(['bash_scripts', 'netmhc_percentile.sh', input_location, output_location])


