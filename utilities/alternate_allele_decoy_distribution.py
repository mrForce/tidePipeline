import argparse
import subprocess
import os

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
parser = argparse.ArgumentParser(description='Get alternate allele decoy distribution')
parser.add_argument('k', type=float, help='Take top k% of the peptides in the target netmhc runs as the targets')
parser.add_argument('output', help='Location of the plot')
parser.add_argument('plot_type', choices=['percent', 'absolute'])
parser.add_argument('--target', help='Path to a NetMHC run. Each line should be of the form: sequence,IC50', action='append')
parser.add_argument('--decoy', help='Path to a NetMHC run. Each line should be of the form: sequence,IC50', action='append')

args = parser.parse_args()
assert(len(args.target))
assert(len(args.decoy))

def merge_and_sort(files):
    #files should be a list of file paths
    proc = subprocess.Popen(['./merge_and_sort.sh', *files], stdout=subprocess.PIPE)
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
    print('outs')
    print(outs)
    output = outs.strip().decode('utf-8')
    print('num lines ')
    print(output)
    return int(output.split(' ')[0])


def take_targets(k, merged_sorted_location):
    nl = num_lines(merged_sorted_location)
    print('nl')
    print(nl)
    num_targets = int(k/100.0*nl)
    print('num targets')
    print(num_targets)
    targets = dict()
    i = 0
    with open(merged_sorted_location, 'r') as f:
        for line in f:
            if len(line) > 1:
                sequence = line.split(',')[0].strip()
                targets[sequence] = i
                if i == num_targets:
                    return targets
                i += 1
    assert(False)

merged_target_candidates = merge_and_sort(args.target)
print(merged_target_candidates)
merged_decoy_candidates = merge_and_sort(args.decoy)
target_dict = take_targets(args.k, merged_target_candidates)
num_targets = len(target_dict)
num_decoys = 0

#If we come across a decoy candidate that is also a target, we don't take it as a decoy. We add the index of the target here (the index is the rank).
matched_decoy_indices = []
with open(merged_decoy_candidates, 'r') as f:
    for line in f:
        if num_decoys >= num_targets:
            break
        split = line.strip().split(',')
        sequence = split[0].strip()
        if sequence in target_dict:
            matched_decoy_indices.append(target_dict[sequence])
        else:
            num_decoys += 1
num_overlap = []
matched_decoy_indices.sort()
print(matched_decoy_indices)
num_overlap.extend([0]*matched_decoy_indices[0])
for i in range(0, len(matched_decoy_indices) - 1):
    index = matched_decoy_indices[i]
    next_index = matched_decoy_indices[i + 1]
    num_overlap.extend([i + 1]*(next_index - index))
num_overlap.extend([num_overlap[-1] + 1]*(num_targets - len(num_overlap) - 1))
if args.plot_type == 'percent':
    for i in range(0, len(num_overlap)):
        num_overlap[i] /= (1.0*i + 1)
fig = plt.figure()

plt.plot(num_overlap)
plt.savefig(args.output)
    
