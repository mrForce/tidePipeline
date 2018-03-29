#include <iostream>
#include <fstream>
#include <set>
#include <string>
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
  std::string line;
  std::set<std::string> peptides;
  std::string sequence;
  int line_length;
  int j;
  std::string temp;
  unsigned long long num_peptides = 0;
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
	      peptides.insert(line.substr(j, len));
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
		peptides.insert(combined);
		//num_peptides++;
		//std::cout << combined << std::endl;
		j++;
	      }
	      j = 0;
	      while(j <= line_length - len){
		peptides.insert(line.substr(j, len));
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
    for(std::set<std::string>::iterator it = peptides.begin(); it != peptides.end(); ++it){
      outFile << *it << std::endl;
      }
    outFile.close();
  }
  return 0;
}

