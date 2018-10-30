#!/bin/bash

(>&2 echo "In sort.sh")
cat $1 | sort | uniq > "$2"
