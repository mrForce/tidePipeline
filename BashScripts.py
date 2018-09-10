import subprocess
import os
import collections
class ParsedNetMHC:
    #row is a row from the NetMHC table
    def __init__(self, project_location, row):
        self.location = os.path.join(project_location, row.PeptideScorePath)
        self.length = row.length()
    def get_location(self):
        return self.location
    def get_length(self):
        return self.length

"""
parsed_netmhc_objects must be a list of ParsedNetMHC instances
"""
def netMHCDecoys(parsed_netmhc_objects, target_location, output_location):
    lengths = line_length_set(target_location)
    netmhc_length_dict = defaultdict(list)
    for x in parsed_netmhc_objects:
        netmhc_length_dict[x.get_length()] = x.get_location()
    for length, locations:
        
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

