cd ..
project="/data1/jordan/PipelineProjects/NetMHCDecoys"
python3 Initialize.py $project murphy_replication/config.ini ~/unimod.xml
python3 AddParamFile.py $project tide-search murphy_replication/tide_search.params default_search_params
python3 AddParamFile.py $project percolator murphy_replication/percolator.params default_percolator_params
python3 AddMGF.py $project /import3/MassSpec/PRAMOD/E.G7-OVA/Aug7_2018/jlb20180807_SKarandikar_20180806EG7prep.mgf PrepMGF
python3 AddMGF.py $project /import3/MassSpec/PRAMOD/E.G7-OVA/Aug7_2018/jlb20180807_SKarandikar_Srivastava_EG7_50ng_MHC1peptides_1uL_60min_Wat25cmBEH_run2.mgf Run2MGF

python3 AddFASTA.py $project health_center_data/mutated_mouse_proteome.fasta MouseProteins
python3 AddHLA.py $project H-2-Kb
python3 AddHLA.py $project H-2-Kd
python3 AddHLA.py $project H-2-Db
python3 AddHLA.py $project H-2-Dd
python3 AddContaminantFile.py $project FASTA health_center_data/contaminants.fasta JeremyContaminants 8 9 10 11

importing_project="/data1/jordan/PipelineProjects/HealthCenter"
python3 ImportPeptideList.py $project $importing_project/peptides/mutated_mouse_proteome.fasta_10.txt MouseProteins MouseProteinTenMers
python3 ImportPeptideList.py $project $importing_project/peptides/mutated_mouse_proteome.fasta_9.txt MouseProteins MouseProteinNineMers
python3 ImportPeptideList.py $project $importing_project/peptides/mutated_mouse_proteome.fasta_8.txt MouseProteins MouseProteinEightMers
python3 ImportPeptideList.py $project $importing_project/peptides/mutated_mouse_proteome.fasta_11.txt MouseProteins MouseProteinElevenMers

python3 ImportNetMHC.py $project $importing_project/NetMHC/11d1f2ff482844aa98ac695ca4e5ec68 H-2-Kb MouseProteinEightMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/6d24e47357244f22a7f71aa51c9c7546 H-2-Kb MouseProteinNineMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/82844164035944939e5230208fe7a6d5 H-2-Kb MouseProteinTenMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/2820fec783e846a2b8907a6aed2a344f H-2-Kb MouseProteinElevenMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/12b9af98cc3541f9b03552a9610c29d7 H-2-Db MouseProteinEightMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/161743ff77e6454086e5cf4919725fb2 H-2-Db MouseProteinNineMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/398b5248d4734fbb859c8a669ae0b2ff H-2-Db MouseProteinTenMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/ad284cc721f143a3ac25f20c942c2b34 H-2-Db MouseProteinElevenMers --rankCutoff 2 --rankCutoff 1

importing_project="/data1/jordan/PipelineProjects/PairwiseOverlap"
python3 ImportNetMHC.py $project $importing_project/NetMHC/0afe925bdf17445588fc2be2fc3116c3 H-2-Kd MouseProteinEightMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/245ebf55e84e414389f86974228216b9 H-2-Kd MouseProteinNineMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/d3b7dafbd5d74886b36f47127582fec6 H-2-Kd MouseProteinTenMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/c8c3d3d8fd4440c7852a050167597698 H-2-Kd MouseProteinElevenMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/8ffce7dd2f2a4f60885dec466357cafb H-2-Dd MouseProteinEightMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/34722eff49de41f984634b47652cb85a H-2-Dd MouseProteinNineMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/1a12d99a3f954a3faf72a7225fe09444 H-2-Dd MouseProteinTenMers --rankCutoff 2 --rankCutoff 1
python3 ImportNetMHC.py $project $importing_project/NetMHC/3fe23b76962e4a03930bb2b11a53297e H-2-Dd MouseProteinElevenMers --rankCutoff 2 --rankCutoff 1



python3 CreateTargetSet.py $project KbTargetSet --FilteredNetMHC MouseProteinEightMers_H-2-Kb_2 --FilteredNetMHC MouseProteinNineMers_H-2-Kb_2 --FilteredNetMHC MouseProteinTenMers_H-2-Kb_2 --FilteredNetMHC MouseProteinElevenMers_H-2-Kb_2

python3 CreateTargetSet.py $project DbTargetSet --FilteredNetMHC MouseProteinEightMers_H-2-Db_2 --FilteredNetMHC MouseProteinNineMers_H-2-Db_2 --FilteredNetMHC MouseProteinTenMers_H-2-Db_2 --FilteredNetMHC MouseProteinElevenMers_H-2-Db_2

python3 CreateTargetSet.py $project Combined --FilteredNetMHC MouseProteinEightMers_H-2-Kb_2 --FilteredNetMHC MouseProteinNineMers_H-2-Kb_2 --FilteredNetMHC MouseProteinTenMers_H-2-Kb_2 --FilteredNetMHC MouseProteinElevenMers_H-2-Kb_2 --FilteredNetMHC MouseProteinEightMers_H-2-Db_2 --FilteredNetMHC MouseProteinNineMers_H-2-Db_2 --FilteredNetMHC MouseProteinTenMers_H-2-Db_2 --FilteredNetMHC MouseProteinElevenMers_H-2-Db_2

python3 CreateTargetSet.py $project CombinedOnePercent --FilteredNetMHC MouseProteinEightMers_H-2-Kb_1 --FilteredNetMHC MouseProteinNineMers_H-2-Kb_1 --FilteredNetMHC MouseProteinTenMers_H-2-Kb_1 --FilteredNetMHC MouseProteinElevenMers_H-2-Kb_1 --FilteredNetMHC MouseProteinEightMers_H-2-Db_1 --FilteredNetMHC MouseProteinNineMers_H-2-Db_1  --FilteredNetMHC MouseProteinTenMers_H-2-Db_1 --FilteredNetMHC MouseProteinElevenMers_H-2-Db_1
