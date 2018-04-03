#include "tdc.h"

/*
class TDCcollection{
 protected:
  std::map<PSM_map_key_, PSM_map_value_> targets_;
  std::map<PSM_map_key_, PSM_map_value_> decoys_;
 public:
  TDCcollection(std::string, std::string);
  std::vector<TargetWithQValue> get_targets(); 
     
  
};
*/

std::vector<std::string> split(std::string parent, std::string substring){
  std::vector<std::string> parts;
  std::size_t index = 0;
  std::size_t start = 0;
  while((index = parent.find_first_of(substring, index)) != std::string::npos){
    parts.append(parent.substr(start, index - start));
    start = index;
  }
  return parts;
}

void TDCcollection::construct_file_index(std::ifstream target_is, std::ifstream decoy_is){
  std::string line;
  int file_index_num = 0;
  while(std::getline(target_is, line)){
    std::vector<std::string> parts = split(line, "\t");
    if(parts.length() == 6){
      std::string file_name = parts[0];
      std::map<std::string, int>::iterator it = file_index_.find(file_name);
      if(it == file_index_.end()){
	file_index_.insert(std::pair<std::string, int>(file_name, file_index_num));
	file_index_num++;
      }
    }else{
      std::cout << "Could not parse line: " << line << std::endl;
    }
  }
  while(std::getline(decoy_is, line)){
    std::vector<std::string> parts = split(line, "\t");
    if(parts.length() == 6){
      std::string file_name = parts[0];
      std::map<std::string, int>::iterator it = file_index_.find(file_name);
      if(it == file_index_.end()){
	file_index_.insert(std::pair<std::string, int>(file_name, file_index_num));
	file_index_num++;
      }
    }else{
      std::cout << "Could not parse line: " << line << std::endl;
    }
  }
}


void TDCcollection::parse_file(std::ifstream input_stream, std::map<PSM_map_key_, PSM_map_value_>& mapper){
    std::string line;
    while(std::getline(target_is, line)){
      std::vector<std::string> parts = split(line, "\t");
      if(parts.length() == 6){
	std::string file_name = parts[0];
	long long scan_number = std::stoll(parts[1]);
	int charge = std::stoi(parts[2]);
	int rank = std::stoi(parts[3]);
	if(rank == 1){
	  double score = std::stod(parts[4]);
	  std::string peptide = parts[5];
	  std::map<std::string, int>::iterator file_index_it = file_index.find(file_name);
	  
	  if(file_index_it != file_index.end()){
	    PSM_map_key_ key(file_index_it->second, scan_number, charge, rank);
	    PSM_map_value_ value(peptide, score);
	    
	    std::pair<> emplace_result = mapper.emplace(key, value);
	    if(!(emplace_result.second)){
	      std::cout << "There should not be duplicate peptides with the same file index, scan, charge and rank: " << line << std::endl;
	    }
	  }else{
	    std::cout << "File name does not have index in line: " << line << std::endl;
	  }
	}
      }else{
	std::cout << "Could not parse line: " << line << std::endl;
      }
    }
}


void TDCcollection::prune_maps(){
  /* The point of this function is to remove:

     1) decoys that do not have a corresponding target (same file index, scan, charge, and rank) 
     2) targets that score worse than the corresponding decoy
     3) decoys that score worse than the corresponding target
  */
  for(std::map<PSM_map_key_, PSM_map_value_>::iterator decoy_iter = decoys_.begin(); decoy_iter != decoys_.end(); ++decoy_iter){
    
  }
}

TDCcollection::TDCcollection(std::string target_location, std::string decoy_location){
  std::ifstream target_is(target_location, std::ifstream::in);  
  std::ifstream decoy_is(decoy_location, std::ifstream::in);
  /* tab seperated values:
     file    scan    charge    rank    score   peptide 
  */
  if(target_is.is_open() && decoy_is.is_open()){
    construct_file_index(target_is, decoy_is);
    target_is.seekg(0, target_is.beg);
    decoy_is.seekg(0, decoy_is.beg);
    parse_file(target_is, targets_);
    parse_file(decoy_is, decoys_);
    prune_maps();
  }
}

std::vector<TargetWithQValue> get_targets(){

}


int main(){
  std::cout << "hello\n";
}
