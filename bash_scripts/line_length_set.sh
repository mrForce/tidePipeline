#!/bin/bash
grep -v -F ">" $1 | awk '{print length($0)}' | sort -n | uniq
