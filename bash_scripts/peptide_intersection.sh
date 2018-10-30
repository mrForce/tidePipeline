#!/bin/bash
(>&2 echo "In peptide_intersection.sh")
numargs=$#
comm -12 $1 $2 > "$3"
