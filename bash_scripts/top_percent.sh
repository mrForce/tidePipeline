#!/bin/bash

#usage: ./top_percent.sh input_file percent output_file
(>&2 echo "In top_percent.sh")
num_lines=$(wc -l < $1)
lines_to_take=$(bc <<< $(wc -l < $1)*$2/100)
sort -t, -k 2,2n -k 1d $1 | head -n $lines_to_take | awk -F ',' '{ print $1 }' > $3

