#include <iostream>
#include <fstream>
#include <set>
#include <string>
#include <functional>
#include <vector>
#include<algorithm>
struct match_t{
  std::string peptide;
  double score;
  double q_value;
  match_t(std::string peptide_, double score_)  {peptide = peptide_; score = score_; q_value = 0;}
  bool operator<(const match_t& match) const {
    return score < match.score;
  }
};

void tdc_procedure(std::vector<match_t> targets, std::vector<match_t> decoys){
  /* Start by sorting them in ascending order */
  std::sort(targets.begin(), targets.end());
  std::sort(decoys.begin(), decoys.end());
  double min_fpr = 1.0;
  size_t num_targets = targets.size();
  size_t num_decoys = decoys.size();
  //this is the number of match_t objects before decoy_iter in the decoys vector
  size_t decoy_iter_num = 0;
  std::vector<match_t>::iterator decoy_iter = decoys.begin();
  size_t target_iter_num = 0;
  for(std::vector<match_t>::iterator target_it = targets.begin(); target_it != targets.end(); ++target_it){
    double target_score = (*target_it).score;
    while((*decoy_iter).score < target_score){
      decoy_iter_num++;
      decoy_iter++;
    }
    size_t num_decoys_above_threshold = num_decoys - decoy_iter_num;
    size_t num_targets_above_threshold = num_targets -  target_iter_num;
    size_t fp = 2*num_decoys_above_threshold;
    size_t tp = num_decoys_above_threshold + num_targets_above_threshold - fp;
    double fpr = 0;
    if(tp + fp == 0){
      fpr = 1.0;
    }else{
      fpr = 1.0*fp/(tp + fp);
    }
    if(fpr < min_fpr){
      min_fpr = fpr;
    }
    (*target_it).q_value = min_fpr;
    target_iter_num++;
  }
  
}

int main(int argc, char* argv[]){
  if(argc != 3){
    std::cout << "Usage: ./tdc targets.txt decoys.txt" << std::endl;
    return 1;
  }
  std::vector<match_t> targets;
  std::vector<match_t> decoys;


  std::ifstream targetFile;
  targetFile.open(argv[1]);
  std::ifstream decoyFile;
  decoyFile.open(argv[2]);
  std::string line;
  size_t tab_location;
  std::string peptide;
  if(targetFile.is_open() && decoyFile.is_open()){
    while(std::getline(targetFile, line)){
      if(line.length() > 0){
        tab_location = line.find("\t");
	peptide = line.substr(0, tab_location);
	targets.emplace_back(peptide, std::stod(line.substr(tab_location + 1, std::string::npos)));
      }
    }
    while(std::getline(decoyFile, line)){
      if(line.length() > 0){
	tab_location = line.find("\t");
	peptide = line.substr(0, tab_location);
	decoys.emplace_back(peptide, std::stod(line.substr(tab_location + 1, std::string::npos)));
      }
    }
  }
  targetFile.close();
  decoyFile.close();
  tdc_procedure(targets, decoys);
  for(std::vector<match_t>::iterator target_it = targets.begin(); target_it != targets.end(); ++target_it){
    std::cout << (*target_it).peptide << std::to_string((*target_it).q_value) << std::endl;
  }
  return 0;
}
