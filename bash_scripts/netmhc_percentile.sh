#!/bin/bash


sort -t, -k2 -r -n $1 | awk -f bash_scripts/percentile.awk $(wc -l < $1) | sort -t, -k2 -n > $2


