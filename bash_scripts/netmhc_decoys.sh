#!/bin/bash
#$1 is the parsed NetMHC output, while $2 are the target peptides
netmhc_peptides=$(mktemp)
decoy_candidates=$(mktemp)
sorted_netmhc=$(mktemp)
peptides_no_fasta_headers=$(mktemp)
output_location = $(mktemp)
sort -t , -k1 $1 > $sorted_netmhc
cat  $sorted_netmhc | awk -F "," '{print $1}' > $netmhc_peptides
grep -v -F ">" $2 | sort > $peptides_no_fasta_headers
comm -23 $netmhc_peptides $peptides_no_fasta_headers > $decoy_candidates
if [[ $(wc -l < $decoy_candidates) -lt $(wc -l < $peptides_no_fasta_headers) ]]; then
    exit 200;
fi
join -t "," $sorted_netmhc $decoy_candidates | sort -n -t , -k2 | awk -F "," '{print $1}' | head -n $(wc -l < $peptides_no_fasta_headers) > $output_location
echo $output_location
rm $netmhc_peptides $decoy_candidates $sorted_netmhc $peptides_no_fasta_headers
#rm $netmhc_peptides $decoy_candidates $sorted_netmhc
#awk '{print">XXX_"NR; print $0}' $temp_output > $3
#awk '{print">"NR; print $0}' $peptides_no_fasta_headers >> $3
#rm  $peptides_no_fasta_headers $temp_output
