#!/bin/bash

#usage: ./top_percent.sh input_file percent output_file
num_lines=$(wc -l < $1)
lines_to_take=$(bc <<< $(wc -l < $1)*$2/100)
sort -t, -k2 -r -n $1 | head -n $lines_to_take | awk -F ',' '{ print $1 }' > $3

