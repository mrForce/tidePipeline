#!/bin/bash
(>&2 echo "Running combined_and_unique_files.sh")
numargs=$#
cat ${@:1: $#-1} | sort | uniq > "${!numargs}"
