BEGIN{
    FOS=",";
    num_lines=ARGV[1];
    last_affinity=-1;
    
    num_peptides_worse_than=0;
    line_number=0
    while(getline < "-"){
	if(($2 + 0) < (last_affinity + 0)){
	    num_peptides_worse_than=line_number;
	    last_affinity=$2;
	}
	if(last_affinity < 0){
	    last_affinity=$2;
	}
	line_number=line_number+1;
	print $1, 100*num_peptides_worse_than/num_lines;
	
    }
}
