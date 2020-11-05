"""


"""
import argparse
import os
import sys
import csv
import math
import re
import subprocess




def write_fasta(output_location, sequences):
    with open(output_location, 'w') as f:
        i = 0
        for x in list(sequences):
            f.write('>%d\n' % i)
            f.write(x + '\n')
            i += 1




peptide_regex = re.compile('^[A-Z\-]\.(?P<peptide>.*)\.[A-Z\-]$')
ptm_removal_regex = re.compile('\[[^\]]*\]')
def parse_peptide(peptide, peptide_regex, ptm_removal_regex):
    match = peptide_regex.match(peptide)
    if match and match.group('peptide'):
        matched_peptide = match.group('peptide')
        return ptm_removal_regex.sub('', matched_peptide)
    else:
        return None
parser = argparse.ArgumentParser(description='Add NetMHC affinity to the output')
parser.add_argument('netmhc')
parser.add_argument('pin_input')
parser.add_argument('pin_output')
parser.add_argument('directory')
parser.add_argument('measure', choices=['IC50', 'logIC50', 'rank'])
parser.add_argument('alleles', nargs='+')
parser.add_argument('--inverse', action='store_true')
parser.add_argument('--best', action='store_true')
args = parser.parse_args()

if args.inverse:
    print('storing inverse')
else:
    print('storing affinity')
"""
Returns a dictionary mapping the peptide to its affinity
"""
def call_netmhc(netmhc_location, directory, peptides, hla, inverse, measure):
    input_location = os.path.join(directory, 'netmhc_input.txt')
    f = open(input_location, 'w')
    output_location = os.path.join(directory, 'netmhc_output.txt')
    for x in peptides:
        f.write(x + '\n')
    f.close()
    command = [netmhc_location, '-a', hla, '-f', input_location, '-p', '-xls', '-xlsfile', output_location]
    print('command: ' + ' '.join(command))
    subprocess.call(command)
    results = {}
    with open(output_location, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        reader.__next__()
        second_row = reader.__next__()
        assert(second_row[1] == 'Peptide')
        assert(second_row[3] == 'nM')
        assert(second_row[4] == 'Rank')
        for row in reader:
            peptide = row[1]
            measure_value = None
            if measure == 'IC50':
                measure_value = float(row[3])
            elif measure == 'logIC50':
                measure_value = math.log10(float(row[3]))
            elif measure == 'rank':
                measure_value = float(row[4])
            if len(peptide.strip()) > 0:
                if inverse:
                    measure_value = 1.0/measure_value                    
                results[peptide.strip()] = str(measure_value)

    return results


netmhc_alleles = args.alleles
#netmhc_alleles = ['HLA-A0201', 'HLA-B0702', 'HLA-C0701']

"""
First, extract the peptides from the PIN file
"""
peptides = set()

with open(args.pin_input, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t', restkey='Proteins')
    next(reader)
    for row in reader:
        peptide = parse_peptide(row['Peptide'], peptide_regex, ptm_removal_regex)
        assert(peptide)
        peptides.add(peptide)

peptide_affinity = {}
for allele in netmhc_alleles:
    peptide_affinity[allele] = call_netmhc(args.netmhc, args.directory, peptides, allele, args.inverse, args.measure)



"""
Insert affinity into PIN output
"""
            
with open(args.pin_input, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t', restkey='Proteins')
    fieldnames = list(reader.fieldnames)
    direction = dict(next(reader))
    if args.best:
        fieldnames.insert(6, 'NetMHC')
        if args.inverse:
            direction['NetMHC'] = '1'
        else:
            direction['NetMHC'] = '-1'
    else:
        for allele in netmhc_alleles:
            fieldnames.insert(6, allele)
            if args.inverse:
                direction[allele] = '1'
            else:
                direction[allele] = '-1'
    with open(args.pin_output, 'w') as g:        
        writer = csv.DictWriter(g, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerow(direction)
        for row in reader:
            peptide = parse_peptide(row['Peptide'], peptide_regex, ptm_removal_regex)
            assert(peptide)
            row_copy = dict(row)
            if args.best:
                row_copy['NetMHC'] = peptide_affinity[netmhc_alleles[0]][peptide]
            for allele in netmhc_alleles:
                if not peptide in peptide_affinity[allele]:
                    print('peptide not present')
                    print(peptide)
                assert(peptide in peptide_affinity[allele])
                if args.best:
                    if args.inverse and float(peptide_affinity[allele][peptide]) > float(row_copy['NetMHC']):
                        row_copy['NetMHC'] = peptide_affinity[allele][peptide]
                    elif not args.inverse and float(peptide_affinity[allele][peptide]) < float(row_copy['NetMHC']):
                        row_copy['NetMHC'] = peptide_affinity[allele][peptide]
                else:
                    row_copy[allele] = peptide_affinity[allele][peptide]
            writer.writerow(row_copy)
    
            
