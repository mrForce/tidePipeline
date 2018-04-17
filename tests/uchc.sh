#!/bin/bash

cd ..
#python3 tPipeInitialize.py EL4Project
#python3 tPipeAddSpecies.py EL4Project mouse
#python3 tPipeAddHLA.py EL4Project H-2-Db mouse

#python3 tPipeAddFASTA.py EL4Project ~/all_mouse_proteins.fasta EL4Proteome


#python3 tPipeAddMGF.py EL4Project "/home/jordan/mgf/160127_609_015_EL4_Y3.mgf" JPRPaper
#These are MGF files for experiments done with immunoprecip H-2Kb
#python3 tPipeAddMGF.py EL4Project "/home/jordan/mgf/jlb20170918_SKarandikar_Srivastatalab_MHCelute_samp1.mgf" ReplicateOne
#python3 tPipeAddMGF.py EL4Project "/home/jordan/mgf/jlb20170918_SKarandikar_Srivastatalab_MHCelute_samp2.mgf" ReplicateTwo

#python3 tPipeAddPeptideList.py EL4Project EightMers EL4Proteome 8
#python3 tPipeAddPeptideList.py EL4Project NineMers EL4Proteome 9
#python3 tPipeAddPeptideList.py EL4Project TenMers EL4Proteome 10
#python3 tPipeAddPeptideList.py EL4Project ElevenMers EL4Proteome 11
#echo "Going to create tide index"
#python3 tPipeCreateTideIndex.py EL4Project mouse_combined_index --netMHCFilter EightMers H-2-Kb 2 --netMHCFilter NineMers H-2-Kb 2 --netMHCFilter TenMers H-2-Kb 2 --netMHCFilter ElevenMers H-2-Kb 2 --netMHCFilter EightMers H-2-Db 2 --netMHCFilter NineMers H-2-Db 2 --netMHCFilter TenMers H-2-Db 2 --netMHCFilter ElevenMers H-2-Db 2 --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme > index_output.txt

#tar -czf index_save.tar.gz EL4Project

#echo "going to run search"

#python3 tPipeRunTideSearch.py EL4Project JPRPaper mouse_combined_index JPRSearchCombined --num-threads 1
#python3 tPipeRunTideSearch.py EL4Project ReplicateOne mouse_combined_index ReplicateOneSearchCombined --num-threads 1
#python3 tPipeRunTideSearch.py EL4Project ReplicateTwo mouse_combined_index ReplicateTwoSearchCombined --num-threads 1

#tar -czf search_save.tar.gz EL4Project

#python3 tPipeRunAssignConfidence.py EL4Project JPRSearchCombined JPRConfidenceCombinedWithSearch
python3 tPipeRunAssignConfidence.py EL4Project ReplicateOneSearchCombined ReplicateOneConfidenceCombinedWithSearch
python3 tPipeRunAssignConfidence.py EL4Project ReplicateTwoSearchCombined ReplicateTwoConfidenceCombinedWithSearch
