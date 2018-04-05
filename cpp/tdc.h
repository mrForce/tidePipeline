#include <string>
#include <map>
#include <vector>
#include <iostream>
#include <fstream>
#include <istream>
#include <algorithm>
#include <math.h>
struct PSM_map_key_{
  int file_index;
  long long scan;
  int charge;
  int rank;
PSM_map_key_(int file_index_, long long scan_, int charge_, int rank_) : file_index(file_index_), scan(scan_), charge(charge_), rank(rank_) {}
  /*
  bool operator< (const PSM_map_key_& lhs, const PSM_map_key_& rhs) {
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
     
     }*/
  bool operator< (const PSM_map_key_& other) const{
    if(other.file_index == file_index){
      if(other.scan == scan){
	if(other.charge == charge){
	  return rank < other.rank;
	}else{
	  return charge < other.charge;
	}
      }else{
	return scan < other.scan;
      }
    }else{
      return file_index < other.file_index;
    }
  }
  

};

struct PSM_map_value_{
  std::string peptide;
  double score;
PSM_map_value_(std::string peptide_, double score_) : peptide(peptide_), score(score_){}
  
};

struct TargetWithQValue{
  /* Apparently PSM_map_key_ is copied by map */
  PSM_map_key_ reference;
  std::string peptide;
  double q_val;
  double fdr;
  double score;
  /*
  bool operator< (const TargetWithQValue& other) const
  {
    return score < other.score;
    }*/
TargetWithQValue(std::string peptide_, PSM_map_key_ reference_, double score_) : peptide(peptide_), score(score_), reference(reference_), q_val(0), fdr(0) {}
TargetWithQValue(TargetWithQValue&& other) : reference(std::move(other.reference)), peptide(std::move(other.peptide)), score(other.score), fdr(other.fdr), q_val(other.q_val){}
  TargetWithQValue& operator=(const TargetWithQValue& other) = default;
};

class TDCcollection{
 protected:
  std::map<PSM_map_key_, PSM_map_value_> targets_;
  std::map<PSM_map_key_, PSM_map_value_> decoys_;
  std::string target_file_;
  std::string decoy_file_;
  std::map<std::string, int> file_index_;
  void parse_file(std::ifstream&, std::map<PSM_map_key_, PSM_map_value_>&);
  void construct_file_index(std::ifstream&, std::ifstream&);
  void prune_maps();
 public:
  TDCcollection(std::string target_location, std::string decoy_location){
      std::ifstream target_is(target_location, std::ifstream::in);  
      std::ifstream decoy_is(decoy_location, std::ifstream::in);
      /* tab seperated values:
	 file    scan    charge    rank    score   peptide 
      */
      if(target_is.is_open() && decoy_is.is_open()){
	construct_file_index(target_is, decoy_is);
	target_is.close();
	target_is.open(target_location, std::ifstream::in);
	decoy_is.close();
	decoy_is.open(decoy_location, std::ifstream::in);
	
	parse_file(target_is, targets_);
	parse_file(decoy_is, decoys_);
	prune_maps();
      }
  }
  std::vector<TargetWithQValue> get_targets();
     
  
};
