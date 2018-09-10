function randindex(n)
{
    return int(n * rand())
}




BEGIN {
    mode=ARGV[2]
    srand()
    while( getline < ARGV[1] ){
	num_indices = NF-1
	if (mode == 0) {
	    _index = randindex(num_indices) + 2
	    print $1 "," $_index
	}else if(mode == 1){
	    min=$2
	    for(i = 3; i <= NF; i++){
		if($i < min){
		    min = $i
		}
	    }
	
	    print $1 "," min
	   
	}else if(mode == 2){e
	    max=$2
	    for(i = 3; i <= NF; i++){
		if($i > max){
		    max = $i
		}
	    }
	    print $1 "," max
	}

    }
}
