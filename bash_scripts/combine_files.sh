#!/bin/bash
(>&2 echo "In combined_files.sh")
numargs=$#
temp=$(mktemp)

cat ${@:1: $#-1} > $temp

mv $temp "${!numargs}"
