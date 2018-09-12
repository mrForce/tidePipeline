#!/bin/bash


sort -t, -k2 -r -n $1 | awk -f percentile.awk $(wc -l < $1) | sort -t, -k2 -n > $2


