#!/bin/bash
#$1 is the combined parsed NetMHC output for the decoy candidates, while $2 are the target peptides, and $3 is the # of decoys needed


#first, we need to sort both alphabetically.
sorted_targets=$(mktemp)
alphabetically_sorted_decoy_candidates=$(mktemp)
decoy_candidates_no_targets=$(mktemp)
output=$(mktemp)
sort $2 > $sorted_targets
sort -t, -k1 $1 > $alphabetically_sorted_decoy_candidates
#remove any target duplicates from the decoys.
join -1 1 -t, -v1 $alphabetically_sorted_decoy_candidates $sorted_targets > $decoy_candidates_no_targets
#resort by IC50, then take head
head -n $3 <(sort -t, -k2 $decoy_candidates_no_targets) | awk -F "," '{print $1}' > $output
echo $output
