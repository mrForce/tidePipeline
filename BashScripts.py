import subprocess

"""

Okay, so here's now this function works. You pass in the locations of the parsed NetMHC output, and peptides (either in peptide format, or FASTA format. We'll remove FASTA headers automatically by grepping for '>'), along with where to put the decoys. The script outputs the top n (ranked via NetMHC ranking) peptides from the NetMHC output that are not shared with target_location. 

It will combine the targets and decoys into a proper FASTA file for MSGF+ to index
"""
def netMHCDecoys(parsed_netmhc_output_location, target_location, output_location):
    assert(subprocess.call(['bash_scripts', 'netmhc_decoys.sh', parsed_netmhc_output_location, target_set_peptides_location, output_location]) == 0)
    
