#!/bin/bash


cat $1 | sort | uniq > "$2"
