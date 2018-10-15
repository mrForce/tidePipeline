#!/bin/bash

(>&2 echo "In netmhc_percentiles.sh")
sort -t, -k2 -r -n $1 | awk -f bash_scripts/percentile.awk $(wc -l < $1) | sort -t, -k2 -n > $2


