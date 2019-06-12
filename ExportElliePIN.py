import Base
import Runners
import PostProcessing
import argparse
import sys
import BashScripts
from pyteomics import mzid
from NetMHC import *
import csv
import os
import tempfile
import DB
import Parsers
parser = argparse.ArgumentParser(description='Export clean PIN files for search, with NetMHC scores appended to specified alleles.')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('search')
parser.add_argument('positive_fdr', type=float)
parser.add_argument('positives_pin')
parser.add_argument('unknown_pin')
parser.add_argument('--allele', help='Name of an allele to run the matches against with NetMHC', action='append')


args = parser.parse_args()

project_folder = args.project_folder



project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
project.begin_command_session()
row = project.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName = args.search).first()
mzid_path = os.path.join(project_folder, row.resultFilePath)
pin_path = os.path.join(project_folder, row.resultFilePath + '.pin')
pin_rw = Parsers.SinglePINRW(pin_path, Parsers.PINParser.msgf_is_target)
pin_parser = Parsers.PINParser(pin_rw, None, 0, 100)
peptide_affinity_map = {}
if args.allele:
    #replace selenocysteine with cysteine
    peptides = []
    for x in pin_parser.get_target_peptides().union(pin_parser.get_decoy_peptides()):
        print('x')
        print(x)
        peptides.append(x.replace('U', 'C'))
    f = tempfile.NamedTemporaryFile()
    with open(f.name, 'w') as g:
        g.write('\n'.join(peptides))
    print('peptides file: %s' % f.name)
    input()
    for peptide in peptides:
        peptide_affinity_map[peptide] = set()
    for allele in args.allele:
        output_file = tempfile.NamedTemporaryFile()
        call_netmhc(project.executables['netmhc'], allele, f.name, output_file.name)
        affinity_file = tempfile.NamedTemporaryFile()
        BashScripts.extract_netmhc_output(output_file.name, affinity_file.name)
        output_file.close()
        with open(affinity_file.name, 'r') as g:
            for line in g:
                if len(line) > 0:
                    line_broken = line.split(',')
                    assert len(line_broken) == 2
                    peptide = line_broken[0]
                    affinity = line_broken[1]
                    peptide_affinity_map[peptide].add((allele, affinity))
        affinity_file.close()
    f.close()

positives_mzid = tempfile.NamedTemporaryFile()
namespace = '{http://psidev.info/psi/pi/mzIdentML/1.1}'
args = parser.parse_args()
m = mzid.MzIdentML(mzid_path)
m.build_tree()
tree = m._tree
identifications = tree.findall('./*/%sAnalysisData/*/%sSpectrumIdentificationResult' % (namespace, namespace))

num_identifications = 0
num_removals = 0

for ident in identifications:
    items = ident.findall('%sSpectrumIdentificationItem' % namespace)
    for item in items:
        q_value = float(item.find('%scvParam[@name=\'MS-GF:QValue\']' % namespace).attrib['value'])
        num_identifications += 1
        if q_value > args.positive_fdr:
            ident.find('..').remove(ident)            
            num_removals += 1
            break

tree.write(positives_mzid.name, xml_declaration=True)

msgf2pin_runner = Runners.MSGF2PinRunner(project.executables['msgf2pin'], os.path.join(project_folder, 'unimod.xml'))
positives_pin = tempfile.NamedTemporaryFile()
head, tail = os.path.split(row.index.MSGFPlusIndexPath)
fasta_index = tail.rfind('.fasta')
new_tail = tail[:fasta_index] + '.revCat.fasta'
fasta_files = [os.path.join(project.project_path, head, new_tail)]
msgf2pin_runner.runConversion(os.path.join(project.project_path, positives_mzid.name), positives_pin.name, fasta_files, 'XXX_')

"""
First clean and add the NetMHC scores to the positives file
"""
print('positives pin')
print(positives_pin.name)
input()
f = open(positives_pin.name, 'r')
positives_reader = csv.DictReader(f, restkey='Proteins', delimiter = '\t')
new_rows = []
for row in positives_reader:
    print('row')
    print(row)
    if row['SpecId'] != 'DefaultDirection':
        if isinstance(row['Proteins'], list):
            temp = ','.join(row['Proteins'])
            row['Proteins'] = temp
        if len(peptide_affinity_map.keys()) > 0:
            peptide = Parsers.PINParser.parse_peptide(row['Peptide'])
            for allele,score in peptide_affinity_map[peptide]:
                row[allele] = score
        new_rows.append(row)
fieldnames = positives_reader.fieldnames
if len(peptide_affinity_map.keys()) > 0:
    fieldnames.extend([x[0] for x in list(peptide_affinity_map.values())[0]])
print('fieldnames')
print(fieldnames)
input()
with open(args.positives_pin, 'w') as g:
    writer = csv.DictWriter(g, fieldnames = fieldnames, delimiter='\t')
    writer.writeheader()
    for row in new_rows:
        writer.writerow(row)
f.close()

f = open(pin_path, 'r')
all_reader = csv.DictReader(f, restkey='Proteins', delimiter = '\t')
new_rows = []
for row in all_reader:
    if row['SpecId'] != 'DefaultDirection':
        if isinstance(row['Proteins'], list):
            temp = ','.join(row['Proteins'])
            row['Proteins'] = temp
        if len(peptide_affinity_map.keys()) > 0:
            peptide = Parsers.PINParser.parse_peptide(row['Peptide'])
            for allele,score in peptide_affinity_map[peptide]:
                row[allele] = score
        new_rows.append(row)
f.close()
with open(args.unknown_pin, 'w') as g:
    writer = csv.DictWriter(g, fieldnames = fieldnames, delimiter='\t')
    writer.writeheader()
    for row in new_rows:
        writer.writerow(row)
project.end_command_session()
