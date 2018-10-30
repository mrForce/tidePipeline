#!/bin/bash


#each file should have a bunch of lines, each of the form: sequence,IC50
merged=$(mktemp)

for file_name in "$@"
do
    cat $file_name >> $merged
    #adds a line seperator
    echo "" >> $merged
done

sorted=$(mktemp)
sort -t, -k2 -n $merged > $sorted
rm $merged
echo $sorted
