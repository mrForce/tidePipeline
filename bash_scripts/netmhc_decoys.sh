#!/bin/bash
#$1 is the parsed NetMHC output, while $2 are the target set peptides, $3 is the output location
netmhc_peptides=$(mktemp)
decoy_candidates=$(mktemp)
sorted_netmhc=$(mktemp) 
sort -t , -k1 $1 > $sorted_netmhc
cat  $sorted_netmhc | awk -F "," '{print $1}' > $netmhc_peptides
comm -23 $netmhc_peptides <(sort $2) > $decoy_candidates
join -t "," $sorted_netmhc $decoy_candidates | sort -n -t , -k2 | awk -F "," '{print $1}' | head -n $(wc -l < $2) > $3
