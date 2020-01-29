#!/bin/bash

cd ..
cd ..
python Initialize.py TargetTestProject tests/target_set/config.ini unimod.xml
python AddHLA.py TargetTestProject H-2-Db
python AddFASTA.py TargetTestProject tests/target_set/long.fasta LongProtein
python AddFASTA.py TargetTestProject tests/target_set/short.fasta ShortProtein
python KChop.py TargetTestProject LongProtein 9 LongProteinNineMers
python KChop.py TargetTestProject ShortProtein 9 ShortProteinNineMers
python RunNetMHC.py TargetTestProject LongProteinNineMers H-2-Db 
python RunNetMHC.py TargetTestProject ShortProteinNineMers H-2-Db
python FilterNetMHC.py TargetTestProject 2.0 filtered LongProteinNineMers_H-2-Db ShortProteinNineMers_H-2-Db 
