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
  bool operator<(const match_t& match) const {
    return score < match.score;
  }
};

void tdc_procedure(std::vector<match_t> targets, std::vector<match_t> decoys){
  /* Start by sorting them in ascending order */
  std::sort(targets.begin(), targets.end());
  std::sort(decoys.begin(), decoys.end());
  double min_fpr = 1.0;
  size_t num_targets = targets.length();
  size_t num_decoys = decoys.length();
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
  std::ifstream inFile;
  inFile.open(argv[1]);
  std::ofstream outFile;
  outFile.open(argv[2]);
  std::string len_string(argv[3]);
  int len = std::stoi(len_string, nullptr);
  return 0;
}

