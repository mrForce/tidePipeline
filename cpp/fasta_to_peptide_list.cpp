#include <iostream>
#include <fstream>
#include <set>
#include <string>
#include <functional>
unsigned long long approx_num_peptides(char* file, int len){
  std::ifstream inFile;
  inFile.open(file);
  unsigned long long num_peptides = 0;
  if(inFile.is_open()){
    std::string line;
    unsigned long long protein_length = 0;
    while(std::getline(inFile, line)){
      if(line.length() > 0){
	if(line[0] == '>'){
	  num_peptides += protein_length + 1 - len;
	  num_peptides++;
	  protein_length = 0;	
	}else{
	  protein_length += line.length();
	}
      }      
    }
  }
  inFile.close();
  return num_peptides;
}

int compare_peptides(char* lhs, char* rhs, int len);
/*
Returns -1 if lhs < rhs
0 if lhs = rhs
1 if lhs > rhs */
int compare_peptides(char* lhs, char* rhs, int len){
  int i = 0;
  while(i < len){
    if(lhs[i] < rhs[i]){
      return -1;
    }else if(lhs[i] > rhs[i]){
      return 1;
    }
    i++;
  }
  return 0;

}
char* partition(char* low, char* high, int len){
  char* i = low - len;
  char* j = high + len;
  char keep_going;
  char k;
  while(true){
    keep_going = true;
    do{
      i += len;
    }while(compare_peptides(i, low, len) == -1);

    do{
      j -= len;
    }while(compare_peptides(j, low, len) == 1);

    if(i >= j){
      return j;
    }
    char temp[len];
    std::copy(i, i + len, temp);
    std::copy(j, j + len, i);
    std::copy(temp, temp + len, j);
  }  
}

void sort(char* low, char* high, int len){
  /*  while(low < high){
    char* part = partition(low, high, len);
    if(high - part < part - low){
      sort(low, part, len);
      low = part + len;
    }else{
      sort(part + len, high, len);
      high = part - len;
    }
    }*/
  if(low < high){
    char* part = partition(low, high, len);
    sort(low, part, len);
    sort(part + len, high, len);
  }
}


int main(int argc, char* argv[]){
  if(argc != 4){
    std::cout << "Usage: ./fasta_to_peptide_list input.fasta output.txt len" << std::endl;
    return 1;
  }

  std::ifstream inFile;
  inFile.open(argv[1]);
  std::ofstream outFile;
  outFile.open(argv[2]);
  std::string len_string(argv[3]);
  int len = std::stoi(len_string, nullptr);
  unsigned long long num_peptides = approx_num_peptides(argv[1], len);
  char* peptide_space = (char*) malloc(num_peptides*sizeof(char)*len);
  char* peptide_pointer = peptide_space;
  auto peptide_compare = [len](const char* lhs, const char* rhs){int i = 0;
								     while(i < len){
    if(lhs[i] < rhs[i]){
      return true;
    }else if(lhs[i] > rhs[i]){
      return false;
    }
    i++;
  }
  //then assume they are equal
  return false;
  };

  std::set<char*, decltype(peptide_compare)> peptides(peptide_compare);
  std::string line;
  std::string sequence;
  int line_length;
  int j;
  std::string temp;

  char new_protein = true;
  if(inFile.is_open() && outFile.is_open()){
    while(std::getline(inFile, line)){
      if(line.length() > 0){
	if(line[0] == '>'){
	  new_protein = true;  
	}else{	  
	  line_length = line.length();
	  if(new_protein){
	    j = 0;
	    while(j <= line_length - len){
	      line.copy(peptide_pointer, len, j);
	      //peptides.insert(peptide_pointer);
	      peptide_pointer += sizeof(char)*len;
	      
	      //std::cout << line.substr(j, len) << std::endl;
	      //num_peptides++;
	      j++;
	    }
	    if(line_length >= len){
	      temp = line.substr(j, len-1);
	    }else{
	      temp = line;
	    }
	    new_protein = false;
	  }else{
	    if(temp.length() + line_length >= len){
	      j = 0;
	      while(j < len - 1 && j < temp.length() && 1 + j <= line_length){
		std::string combined;
		combined.append(temp.substr(j, std::string::npos));
		combined.append(line.substr(0, 1 + j));
		line.copy(peptide_pointer, len, j);
		//peptides.insert(peptide_pointer);
		peptide_pointer += len*sizeof(char);
		//peptides.insert(combined);
		//num_peptides++;
		//std::cout << combined << std::endl;
		j++;
	      }
	      j = 0;
	      while(j <= line_length - len){
		line.copy(peptide_pointer, len, j);
		//peptides.insert(peptide_pointer);
		peptide_pointer += len*sizeof(char);
		j++;
	      }
	      //we want the len-1 last characters of the line
	      if(line_length >= len){
		temp = line.substr(j, len - 1);	  
	      }else{
		temp = line;
	      }
	    }else{
	      temp.append(line);
	    }
	  }
	}
	
      }
    }
    inFile.close();
    std::string temp;
    
    temp.clear();    
    /*for(std::set<char*>::iterator it = peptides.begin(); it != peptides.end(); ++it){
      temp.assign(*it, len);
      outFile << temp << std::endl;
      }*/
    sort(peptide_space, peptide_pointer, len);
    for(char* it = peptide_space; it < peptide_pointer; it += len*sizeof(char)){
      temp.assign(it, len);
      outFile << temp << std::endl;
    }
    outFile.close();
  }
  return 0;
}

