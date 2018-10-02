#!/bin/bash

numargs=$#
temp=$(mktemp)

cat ${@:1: $#-1} > $temp

mv $temp "${!numargs}"
