class Error(Exception):
    pass

class CustomError(Exception):
    def __init__(self, thing):
        self.thing = thing
    def __repr__(self):
        return self.prefix + self.thing + self.suffix
    def __str__(self):
        return self.__repr__()
    @staticmethod
    def factory(name, prefix, suffix):
        return type(name, (Error,), {'prefix': prefix, 'suffix': suffix})

InvalidSearchTypeError = CustomError.factory('InvalidSearchTypeError', '', ' is an invalid search type')
ParameterFileNameMustBeUniqueError = CustomError.factory('ParameterFileNameMustBeUniqueError', 'There is already a parameter file with the name: ', ' . It must be unique')
NoSuchPercolatorParameterFileError = CustomError.factory('NoSuchPercolatorParameterFileError', 'There is no percolator parameter file with the name: ', '')
DidNotFindUniquePercolatorNameError = CustomError.factory('DidNotFindUniquePercolatorNameError', 'Program came up with name for new percolator row: ', ' but it was not actually unique. This is a bug, please report it')

FileMarkedForDeletionDoesNotExistError = CustomError.factory('FileMarkedForDeletionDoesNotExistError', 'File marked for deletion: ', ' does not exist, so it cannot be deleted!')
DirectoryMarkedForDeletionDoesNotExistError = CustomError.factory('DirectoryMarkedForDeletionDoesNotExistError', 'Directory marked for deletion: ', ' does not exist, so it cannot be deleted!')

TideSearchLinkedToMSGFPlusIterativeError = CustomError.factory('TideSearchLinkedToMSGFPlusIterativeError', 'The TideSearch: ', ' is linked to an MSGF+ iterative search')

MSGFPlusSearchLinkedToTideIterativeError = CustomError.factory('MSGFPlusSearchLinkedToTideIterativeError', 'The MSGF+ Search: ', ' is linked to a Tide Iterative Search')

class AWKFailedError(Error):
    def __init__(self, command):
        self.command = command
    def __repr__(self):
        return 'awk command: ' + ' '.join(self.command) + ' failed'

class SedFailedError(Error):
    def __init__(self, command):
        self.command = command
    def __repr__(self):
        return 'sed command: ' + ' '.join(self.command) + ' failed'



class DifferentScoresForSamePeptidesError(Error):
    def __init__(self, peptide_to_score_map):
        self.peptide_to_score_map = peptide_to_score_map
    def __repr__(self):
        return 'The following peptides were given the following (different) scores: \n%s ' % '\n'.join([k + ', '.join(v) for k,v in self.peptide_to_score_map.items()])
class NonZeroReturnCodeError(Error):
    def __init__(self, command, code):
        self.command = command
        self.code = code
    def __repr__(self):
        return 'command: %s returned non-zero code: %d' % (' '.join(self.command), self.code)
class NoPathInMSGFPlusTrainingOutput(Error):
    def __init__(self):
        pass
    def __repr__(self):
        return 'No output path found in MSGF+ training output'

class MSGFPlusTrainingFailedError(Error):
    def __init__(self, command):
        self.command = command
    def __repr__(self):
        return 'Failed to run MSGF+ Training using the command: ' + self.command
    
class BothDecoyTypeAndNetMHCDecoysSpecifiedError(Error):
    def __init__(self):
        pass
    def __repr__(self):
        return 'Both the decoy_type and netmhc_decoys were specified. They are mutually exclusive options'
class InvalidDecoyTypeError(Error):
    def __init__(self, decoy_type, possible_types):
        self.decoy_type = decoy_type
        self.possible_types = possible_types
    def __repr__(self):
        return 'Decoy type is: ' + str(self.decoy_type) + ', which is invalid. It must be one of: ' + str(self.possible_types)


class DuplicateNetMHCError(Error):
    def __init__(self, peptide_list_name, hla):
        self.peptide_list_name = peptide_list_name
        self.hla = hla
    def __repr__(self):
        return 'There is already a NetMHC run for PeptideList: ' + self.peptide_list_name + ' and HLA: ' + self.hla
class MSGF2PinFailedError(Error):
    def __init__(self, command):
        self.command = command
    def __repr__(self):
        return 'The MSGF2Pin call failed: ' + self.command


class RAWFileDoesNotExistError(Error):
    def __init__(self, raw_name):
        self.raw_name = raw_name
    def __repr__(self):
        return 'There is no RAW file with name: ' + self.raw_name


class RAWNameMustBeUniqueError(Error):
    def __init__(self, raw_name):
        self.raw_name = raw_name
    def __repr__(self):
        return 'There is already a RAW file with name: ' + self.raw_name
class MaxQuantParamFileMustBeUniqueError(Error):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'There is already a MaxQuant Parameter file with name: ' + self.name

    
class MSGFPlusIndexFailedError(Error):
    def __init__(self, command):
        self.command = command
    def __repr__(self):
        return 'Failed to create MSGFPlus index using the command: ' + self.command

class NoSuchMSGFPlusIndexError(Error):
    def __init__(self, command):
        self.command = command
    def __repr__(self):
        return 'No such MSGF+ Index in command: ' + self.command
class MSGFPlusSearchFailedError(Error):
    def __init__(self, command):
        self.command = command
    def __repr__(self):
        return 'Failed to run MSGF+ Search using the command: ' + self.command
    
class MaxQuantSearchFailedError(Error):
    def __init__(self, command):
        self.command = command
    def __repr__(self):
        return 'Failed to run MaxQuant Search using the command: ' + self.command
    
class NoSuchTargetSetError(Error):
    def __init__(self, target_set_name):
        self.target_set_name = target_set_name
    def __repr__(self):
        return 'There is no TargetSet with the name: ' + self.target_set_name


class TargetSetNameMustBeUniqueError(Error):
    def __init__(self, target_set_name):
        self.target_set_name = target_set_name
    def __repr__(self):
        return 'There is already a TargetSet with the name: ' + self.target_set_name


class NoSuchFilteredNetMHCError(Error):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'There is no FilteredNetMHC entry with the name: ' + self.name

class TideSearchRowDoesNotExistError(Error):
    def __init__(self, tide_search_name):
        self.tide_search_name = tide_search_name
    def __repr__(self):
        return 'There is no TideSearch row with the name: ' + str(self.tide_search_name)


class MSGFPlusSearchRowDoesNotExistError(Error):
    def __init__(self, search_name):
        self.search_name = search_name
    def __repr__(self):
        return 'There is no MSGFPlusSearch row with the name: ' + str(self.search_name)

class FilteredSearchResultNameMustBeUniqueError(Error):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'There is already a FilteredSearchResult with the name: ' + self.name
class AssignConfidenceNameMustBeUniqueError(Error):
    def __init__(self, assign_confidence_name):
        self.assign_confidence_name = assign_confidence_name
    def __repr__(self):
        return 'There is already an AssignConfidence row with the name: ' + str(self.assign_confidence_name)
    
class PercolatorNameMustBeUniqueError(Error):
    def __init__(self, percolator_name):
        self.percolator_name = percolator_name
    def __repr__(self):
        return 'There is already a Percolator row with the name: ' + str(self.percolator_name)

class AssignConfidenceFailedError(Error):
    def __init__(self, command):
        self.message = 'assign-confidence command: ' + command + ' failed'
    def __repr__(self):
        return self.message


class PercolatorFailedError(Error):
    def __init__(self, command):
        self.message = 'percolator command: ' + command + ' failed'
    def __repr__(self):
        return self.message

class MGFFileMissingError(Error):
    def __init__(self, idMGFfile, name, path):
        self.message = 'MGF file with ID: ' + str(idMGFfile) + ' and name: ' + name + ' and path: ' + path + ' is missing'
    def __repr__(self):
        return self.message
    
class ProjectPathAlreadyExistsError(Error):
    def __init__(self, project_folder):
        self.message = 'Project folder ' + project_folder + ' already exists.'
    def __repr__(self):
        return self.message
class FASTAWithNameAlreadyExistsError(Error):
    def __init__(self, name):
        self.message = 'There\'s already a FASTA file with the name: ' + name + ' in the database'
    def __repr__(self):
        return self.message

class UniprotMapperWithNameAlreadyExistsError(Error):
    def __init__(self, name):
        self.message = 'There\'s already a Uniprot Mapper file with the name: ' + name + ' in the database'
    def __repr__(self):
        return self.message

class TPMFileWithNameAlreadyExistsError(Error):
    def __init__(self, name):
        self.message = 'There\'s already a TPM file with the name: ' + name + ' in the database'
    def __repr__(self):
        return self.message
    
class FileDoesNotExistError(Error):
    def __init__(self, filepath):
        self.message = 'File with path: ' + filepath + ' does not exist'
    def __repr__(self):
        return self.message
class FASTAWithNameDoesNotExistError(Error):
    def __init__(self, name):
        self.message = 'There is no FASTA entry with the name: ' + name

    def __repr__(self):
        return self.message
class HLAWithNameExistsError(Error):
    def __init__(self, hla_name):
        self.message = 'There is already an HLA with the name: ' + hla_name
    def __repr__(self):
        return self.message
class NoSuchSpeciesError(Error):
    def __init__(self, species_name):
        self.message = 'There is no species with the name: ' + species_name
    def __repr__(self):
        return self.message
class MultipleSpeciesWithSameNameError(Error):
    def __init__(self, species_name):
        self.message = 'There are multiple species with the name: ' + species_name
    def __repr__(self):
        return self.message
class NoSpeciesWithNameError(Error):
    def __init__(self, species_name):
        self.message = 'There are no species with the name: ' + species_name
    def __repr__(self):
        return self.message
class NoSpeciesWithIDError(Error):
    def __init__(self, species_id):
        self.message = 'There are no species with the ID: ' + str(species_id)
    def __repr__(self):
        return self.message
class MultipleSpeciesWithSameIDError(Error):
    def __init__(self, species_id):
        self.message = 'There are multiple species with the ID: ' + species_id
    def __repr__(self):
        return self.message

class NotProperFASTAFileError(Error):
    def __init__(self, path):
        self.message = 'The file at found at: ' + path + ' could not be parsed as a FASTA file'
    def __repr__(self):
        return self.message
class FASTAMissingError(Error):
    def __init__(self, fasta_id, fasta_name, path):
        self.message = 'The row in the FASTA table, with id: ' + str(fasta_id) + ' and name: ' + str(fasta_name) + ' points to a FASTA file with path: ' + path + ', but this file does not exist.'
    def __repr__(self):
        return self.message

class OperationsLockedError(Error):
    def __init__(self):
        self.message = 'The operation lock file (operation_lock) exists, so we cannot do anything with this project at the moment'
    def __repr__(self):
        return self.message
class NoSuchPeptideListError(Error):
    def __init__(self, peptide_list_name):
        self.message = 'There is no row in the PeptideList table with the name: ' + peptide_list_name

    def __repr__(self):
        return self.message

class NoSuchFASTAError(Error):
    def __init__(self, fasta_name):
        self.message = 'There is no row in the FASTA table with the name: ' + fasta_name

    def __repr__(self):
        return self.message

class NoSuchHLAError(Error):
    def __init__(self, hla_name):
        self.message = 'There is no HLA with the name: ' + hla_name
    def __repr__(self):
        return self.message

class PeptideListFileMissingError(Error):
    def __init__(self, peptide_list_id, peptide_list_name, path):
        self.message = 'The row in the PeptideList table, with id: ' + str(peptide_list_id) + ' and name: ' + str(peptide_list_name) + ' points to a peptide file with path: ' + path + ', but this file does not exist.'
    def __repr__(self):
        return self.message

class MGFRowDoesNotExistError(Error):
    def __init__(self, name):
        self.message = 'There is no MGF file with the name: ' + name

    def __repr__(self):
        return self.message
class MGFNameMustBeUniqueError(Error):
    def __init__(self, name):
        self.message = 'There\'s already an MGF file with the name: ' + name

    def __repr__(self):
        return self.message
    
class TideIndexFailedError(Error):
    def __init__(self, command):
        self.message = 'The tide-search command ended: ' + command + ' with non-zero exit code'
    def __repr__(self):
        return self.message


class NoSuchTideIndexError(Error):
    def __init__(self, name):
        self.message = 'There is no tide index with the name: ' + name
    def __repr__(self):
        return self.message
class TideSearchFailedError(Error):
    def __init__(self, command):
        self.message = 'The tide-search command ended: ' + command + ' with non-zero exit code'
    def __repr__(self):
        return self.message

class TideSearchNameMustBeUniqueError(Error):
    def __init__(self, name):
        self.message = 'There is already a Tide Search with the name: ' + name
    def __repr__(self):
        return self.message

class MSGFPlusSearchNameMustBeUniqueError(Error):
    def __init__(self, name):
        self.message = 'There is already an MSGF+ Search with the name: ' + name
    def __repr__(self):
        return self.message

    
class InvalidParameterLineError(Error):
    def __init__(self, line):
        self.message = 'The line does not follow the format for a percolator parameter file: ' + line
    def __repr__(self):
        return self.message
