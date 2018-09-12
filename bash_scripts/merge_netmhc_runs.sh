#!/bin/bash

chainJoin(){

    if [ "$#" -eq 1 ]; then
	sort -t, -k1 $1
    else
	join -t "," <(sort -t, -k1 $1) <( sort -t, -k1 <( chainJoin  ${@:2} ) )
    fi
}


if [ $# -lt 4 ]; then
    echo "Usage: merge_netmhc_runs.sh mode output netmhc_run_1 netmhc_run_2...\n where mode is 0 if we want to randomly select the rank to use; if 1, then select lowest (best) rank; if 2 then select greatest (worst) rank"
else
    fileArgs=${@:3: $#-1}
    joined=$(mktemp)
    chainJoin $fileArgs > $joined
    awk -F "," -f bash_scripts/select_netmhc_rank.awk $joined $1 
fi
