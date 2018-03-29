from Bio import SeqIO
import re
import subprocess
import sys
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

input_file = sys.argv[1]
output_file = sys.argv[2]
length = int(sys.argv[3])
peptides = extract_peptides(input_file, length)
write_peptides(output_file, peptides)
