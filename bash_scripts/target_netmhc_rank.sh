#!/bin/bash

#$1 is the path of a file containing the target peptides. $2 is the file to output the rank to, $3 is the file to output the IC50 to. $4 and beyond are paths to the parsed NetMHC Runs (those with the -affinity suffix).

(>&2 echo "In target_netmhc.sh")
num_lines=$(wc -l $1 | cut -f1 -d' ')
join -1 1 -2 1  -t , <( sort -k1 $1) <( cat ${@:4: $#} | sort -t, -k1) > $3
sort -k2 -t, -n -r | awk -v num_lines=$num_lines 'BEGIN{FS=","; OFS=","} {print $1, NR/num_lines}' > $2




