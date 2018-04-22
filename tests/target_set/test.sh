#!/bin/bash

cd ..
cd ..
python tPipeInitialize.py TargetTestProject
python tPipeAddHLA.py TargetTestProject H-2-Db
python tPipeAddFASTA.py TargetTestProject tests/target_set/long.fasta LongProtein
python tPipeAddFASTA.py TargetTestProject tests/target_set/short.fasta ShortProtein
python tPipeAddPeptideList.py TargetTestProject LongProtein 9 LongProteinNineMers
python tPipeAddPeptideList.py TargetTestProject ShortProtein 9 ShortProteinNineMers
python tPipeRunNetMHC.py TargetTestProject LongProteinNineMers H-2-Db 2.0 LongProteinH_2_Db
python tPipeCreateTargetSet.py TargetTestProject --PeptideList ShortProteinNineMers --FilteredNetMHC LongProteinH_2_Db combined_targets
python tPipeCreateTideIndex.py TargetTestProject TargetSet combined_targets combined_index
