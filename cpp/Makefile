all: fasta_to_peptide_list tdc

fasta_to_peptide_list: fasta_to_peptide_list.o
	g++  -g fasta_to_peptide_list.o -o fasta_to_peptide_list
fasta_to_peptide_list.o: fasta_to_peptide_list.cpp
	g++ -g -c fasta_to_peptide_list.cpp

tdc: tdc.o
	g++  -g tdc.o -o tdc
tdc.o: tdc.cpp
	g++ -g -c tdc.cpp

clean:
	rm *.o fasta_to_peptide_list tdc
