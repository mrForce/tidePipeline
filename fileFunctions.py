from Bio import SeqIO
import re
import subprocess

def extract_peptides(fasta_path, length):
    peptides = set()
    with open(fasta_path, 'rU') as handle:
        for record in SeqIO.parse(handle, 'fasta'):
            sequence = record.seq
            if len(sequence) >= length:
                for i in range(0, len(sequence) - length + 1):
                    peptide = sequence[i:(i + length)]
                    peptides.add(str(peptide))
    return peptides

def write_peptides(file_path, peptide_set):
    peptide_list = list(peptide_set)
    with open(file_path, 'w') as f:
        for x in peptide_list:
            f.write(x + '\n')
def parse_netmhc(output_file):
    regex = re.compile('^(\s+[^\s]+){2}(\s+(?P<peptide>[A-Z]+))(\s+[^\s]+){10}(\s+(?P<rank>[0-9]{1,2}\.[0-9]+))')
    results = []
    with open(output_file, 'r') as f:
        for line in f:
            match = regex.match(line)
            if match:
                results.append((match.group('peptide'), float(match.group('rank'))))
    return results

def call_netmhc(hla, peptide_file_path, output_path):
    with open(output_path, 'w') as f:
        subprocess.run(['netmhc', '-a', hla, '-f', peptide_file_path, '-p'], stdout=f)
