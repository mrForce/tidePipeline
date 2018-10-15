#!/bin/bash
(>&2 echo "In line_length_set.sh")
grep -v -F ">" $1 | awk '{print length($0)}' | sort -n | uniq
