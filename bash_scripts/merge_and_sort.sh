#!/bin/bash
(>&2 echo "In merge_and_sort.sh")

#each file should have a bunch of lines, each of the form: sequence,IC50
merged=$(mktemp)
sort $1 > $merged
for file_name in ${@:2}
do
    temp_merged=$(mktemp)
    join -t, -1 1 -2 1 -a 1 -a 2 $merged <(sort $file_name) > $temp_merged
    mv $temp_merged $merged    
done

final_merged=$(mktemp)
awk -f bash_scripts/select_netmhc_rank.awk -F, $merged 1 > $final_merged
rm $merged
sorted=$(mktemp)
#the sed call removes any whitespace lines.
sort -t, -k2 -n $final_merged | sed '/^\s*$/d' > $sorted
rm $final_merged
echo $sorted
