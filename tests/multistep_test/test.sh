#!/bin/bash

cd ..
cd ..
python3 Initialize.py multistep_project tests/multistep_test/config.ini unimod.xml
python3 AddHLA.py multistep_project H-2-Kb
python3 AddFASTA.py multistep_project tests/multistep_test/short.fasta MouseProteins
python3 KChop.py multistep_project MouseProteins 9 MouseProteinNineMers
python3 AddMGF.py multistep_project  tests/Y3Test/160127_609_015_EL4_Y3.mgf Y3_mgf 0 2 3
python3 RunNetMHC.py multistep_project MouseProteinNineMers H-2-Kb --rank 2
python3 CreateMSGFPlusIndex.py multistep_project FilteredNetMHC MouseProteinNineMers_H-2-Kb_2 NineMerH2KbTwoPercentIndex
python3 CreateMSGFPlusIndex.py multistep_project FASTA MouseProteins MouseProteinsIndex
zip -r MultistepSearch.zip multistep_project
python3 AddParamFile.py multistep_project percolator tests/multistep_test/percolator.params percolator
python3 RunIterativeMSGFPlusSearch.py multistep_project Y3_mgf 0.01 IterativeTestSearch MouseProteinsIndex NineMerH2KbTwoPercentIndex --use_percolator percolator
python3 ExportPeptides.py multistep_project MSGFPlusIterativeSearch IterativeTestSearch msgf_iterative_peptides.txt
