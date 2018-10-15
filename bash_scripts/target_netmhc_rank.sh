#!/bin/bash

#$1 is the path of a file containing the target peptides. $2 is the file to output it to. $3 and beyond are paths to the parsed NetMHC Runs (those with the -affinity suffix).

(>&2 echo "In target_netmhc.sh")
num_lines=$(wc -l $1 | cut -f1 -d' ')
join -1 1 -2 1  -t , <( sort -k1 $1) <( cat ${@:3: $#} | sort -t, -k1) | sort -k2 -t, -n -r | awk -v num_lines=$num_lines 'BEGIN{FS=","; OFS=","} {print $1, NR/num_lines}' > $2




