#!/bin/bash
numargs=$#
cat ${@:1: $#-1} | sort | uniq | awk '{print">"NR; print $0}' > "${!numargs}"
