BEGIN{
    OFS=",";
    peptide_index = -1
    affinity_index = -1
    while(getline < ARGV[1]){
	if($0 ~ /^[^-#]/){
	    if(peptide_index == -1 && affinity_index == -1){
		for(i = 1; i <= NF; i++){
		    if($i ~ /Affinity/){
		        affinity_index= i
		    }
		    if($i ~ /peptide/){
			peptide_index = i
		    }
		}
	    }else{
		print $peptide_index, $affinity_index > ARGV[2]
	    }
	}
	    

    }
    
}
