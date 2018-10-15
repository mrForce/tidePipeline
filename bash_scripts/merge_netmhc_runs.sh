#!/bin/bash
(>&2 echo "In merge_netmhc_runs.sh")
chainJoin(){

    if [ "$#" -eq 1 ]; then
	sort -t, -k1 $1
    else
	join -t "," <(sort -t, -k1 $1) <( sort -t, -k1 <( chainJoin  ${@:2} ) )
    fi
}


if [ $# -lt 4 ]; then
    echo "Usage: merge_netmhc_runs.sh mode netmhc_run_1 netmhc_run_2...\n where mode is 0 if we want to randomly select the rank to use; if 1, then select lowest (best) rank; if 2 then select greatest (worst) rank"
else
    fileArgs=${@:2: $#-1}
    joined=$(mktemp)
    chainJoin $fileArgs > $joined
    
    output=$(mktemp)
    echo $(pwd) 1&>&2
    awk -F "," -f bash_scripts/select_netmhc_rank.awk $joined $1 > $output
    echo $output
    rm $joined
fi
