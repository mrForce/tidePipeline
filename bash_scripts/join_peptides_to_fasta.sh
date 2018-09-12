#!/bin/bash


while getopts ":P:" opt; do
    case $opt in
	P)
	    prefix=$OPTARG
	    ;;
	\?)
	    echo "invalid option"
	    exit 1
	    ;;
	:)
	    prefix=""
	    ;;

    esac
    

done


numargs=$#

end=$(expr $numargs - $OPTIND)

cat ${@:$OPTIND:end} | sort | uniq  | awk -v prefix="$prefix" '{print ">"prefix NR; print $0}' > "${!numargs}"
