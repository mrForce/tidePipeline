BEGIN{
    OFS=",";
    peptide_index = -1
    affinity_index = -1
    #set this when pos, Affinity and peptide are in line.
    seperator_depth=-1
    while(getline < ARGV[1]){
	
	if(seperator_depth==-1 && $0 ~ /pos/ && $0 ~ /Affinity/ && $0 ~ /peptide/){
	    seperator_depth = 0
	    for(i = 1; i <= NF; i++){
		if($i ~ /Affinity/){
		    affinity_index=i
		}
		if($i ~ /peptide/){
		    peptide_index=i
		}
	    }

	}else if(seperator_depth == 0 && $0 ~ /--------/){

	    seperator_depth = 1
	}else if(seperator_depth == 1 && $0 ~ /--------/){

	    seperator_depth = -1
	}else if(seperator_depth == 1 && $0 ~ /^[^-#]/){
	    print $peptide_index, $affinity_index > ARGV[2]
	}
	    

    }
    
}
