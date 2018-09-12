#!/bin/bash


sort -t, -k2 -r -n $1 | awk -F "," -f percentile.awk $(wc -l < $1)


