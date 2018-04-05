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
    parts.push_back(parent.substr(start, index - start));
    start = index;
  }
  return parts;
}


/* Just to be clear: although it looks similar to parse_file, they are not interchange-able! */
void TDCcollection::construct_file_index(std::ifstream& target_is, std::ifstream& decoy_is){
  std::string line;
  int file_index_num = 0;
  while(std::getline(target_is, line)){
    std::vector<std::string> parts = split(line, "\t");
    if(parts.size() == 6){
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
    if(parts.size() == 6){
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


void TDCcollection::parse_file(std::ifstream& input_stream, std::map<PSM_map_key_, PSM_map_value_>& mapper){
    std::string line;
    while(std::getline(input_stream, line)){
      std::vector<std::string> parts = split(line, "\t");
      if(parts.size() == 6){
	std::string file_name = parts[0];
	long long scan_number = std::stoll(parts[1]);
	int charge = std::stoi(parts[2]);
	int rank = std::stoi(parts[3]);
	if(rank == 1){
	  double score = std::stod(parts[4]);
	  std::string peptide = parts[5];
	  std::map<std::string, int>::iterator file_index_it = file_index_.find(file_name);
	  
	  if(file_index_it != file_index_.end()){
	    PSM_map_key_ key(file_index_it->second, scan_number, charge, rank);
	    PSM_map_value_ value(peptide, score);
	    
	    std::pair<std::map<PSM_map_key_, PSM_map_value_>::iterator, bool> emplace_result = mapper.emplace(key, value);
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
  std::map<PSM_map_key_, PSM_map_value_>::iterator decoy_iter = decoys_.begin();
  while(decoy_iter != decoys_.end()){
    PSM_map_key_ key = decoy_iter->first;
    auto target_iter = targets_.find(key);
    if(target_iter != targets_.end()){
      double target_score = target_iter->second.score;
      double decoy_score = decoy_iter->second.score;
      
      if(fabs(target_score - decoy_score) < 1e-10){
	//break ties randomly
	int select = rand() % 2;
	if(select == 0){
	  //then remove decoy
	  decoy_iter = decoys_.erase(decoy_iter);
	}else{
	  targets_.erase(target_iter);
	  decoy_iter++;
	}
      }else if(target_score > decoy_score){
	decoy_iter = decoys_.erase(decoy_iter);
      }else{
	targets_.erase(target_iter);
	decoy_iter++;
      }
    }else{
      decoy_iter = decoys_.erase(decoy_iter);
    }
  }
 

}
/*
TDCcollection::TDCcollection(std::string target_location, std::string decoy_location){
}*/

std::vector<TargetWithQValue> TDCcollection::get_targets(){
  std::vector<TargetWithQValue> target_scores;
  std::vector<double> decoy_scores;
  for(std::map<PSM_map_key_, PSM_map_value_>::iterator it = targets_.begin(); it != targets_.end(); ++it){
    target_scores.emplace_back(it->second.peptide, it->first, it->second.score);
  }
  for(auto it = decoys_.begin(); it != decoys_.end(); ++it){
    decoy_scores.push_back(it->second.score);
  }
  std::sort(target_scores.begin(), target_scores.end(), [](const TargetWithQValue& a, const TargetWithQValue& b) {return a.score < b.score;});
  std::sort(decoy_scores.begin(), decoy_scores.end());
  std::size_t decoy_index = 0;
  std::size_t target_index;
  double fdr;
  for(target_index = 0; target_index < target_scores.size(); target_index++){
    while(decoy_index < decoy_scores.size() && decoy_scores[decoy_index] <= target_scores[target_index].score){
      decoy_index++;
    }
    fdr = ((double)(decoy_index + 1))/((double)(target_index + 1));
    if(fdr > 1.0){
      fdr = 1.0;
    }
    target_scores[target_index].fdr = fdr;
  }
  auto target_score_iterator = target_scores.end();
  double last_fdr = fdr;
  target_score_iterator--;

  for(; target_score_iterator != target_scores.begin(); target_score_iterator--){
    fdr = target_score_iterator->fdr;
    if(last_fdr < fdr){
      target_score_iterator->q_val = last_fdr;     
    }
    last_fdr = target_score_iterator->q_val;
  }
  return target_scores;
  
}


int main(){
  std::cout << "hello\n";
}
