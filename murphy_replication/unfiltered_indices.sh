#!/bin/bash
cd ..
python3 CreateTargetSet.py MurphyReplication --PeptideList MouseProteinEightMers --PeptideList MouseProteinNineMers --PeptideList MouseProteinTenMers --PeptideList MouseProteinElevenMers CombinedUnfiltered
python3 CreateTideIndex.py MurphyReplication TargetSet CombinedUnfiltered CombinedUnfilteredIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme

