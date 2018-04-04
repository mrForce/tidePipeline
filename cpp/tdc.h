#include <string>
#include <map>
#include <vector>
#include <iostream>
#include <fstream>
#include <math.h>
struct PSM_map_key_{
  int file_index;
  long long scan;
  int charge;
  int rank;
PSM_map_key_(int file_index_, long long scan_, int charge_, int rank_) : file_index(file_index_), scan(scan_), charge(charge_), rank(rank_) {}
  bool operator() (const PSM_map_key_& lhs, const PSM_map_key_& rhs) const
   {
     if(lhs.file_index == rhs.file_index){
       if(lhs.scan == rhs.scan){
	 if(lhs.charge == rhs.charge){
	   return lhs.rank < rhs.rank;
	 }else{
	   return lhs.charge < rhs.charge;
	 }
       }else{
	 return lhs.scan < rhs.scan;
       }
     }else{
       return lhs.file_index < rhs.file_index;
     }
     
   }
};

struct PSM_map_value_{
  std::string peptide;
  double score;
PSM_map_value_(std::string peptide_, double score_) : peptide(peptide_), score(score_){}
  
};

struct TargetWithQValue{
  PSM_map_key_& reference;
  std::string peptide;
  double q_val;
};

class TDCcollection{
 protected:
  std::map<PSM_map_key_, PSM_map_value_> targets_;
  std::map<PSM_map_key_, PSM_map_value_> decoys_;
  std::string target_file_;
  std::string decoy_file_;
  std::map<std::string, int> file_index_;
  void parse_file(std::ifstream, std::map<PSM_map_key_, PSM_map_value_>&);
  void construct_file_index(std::ifstream, std::ifstream);
  void prune_maps();
 public:
  TDCcollection(std::string, std::string);
  std::vector<TargetWithQValue> get_targets(); 
     
  
};
