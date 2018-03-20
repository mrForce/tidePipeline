import tPipeDB
import os

class Error(Exception):
    pass

class ProjectPathAlreadyExistsError(Error):
    def __init__(self, project_folder):
        self.message = 'Project folder ' + project_folder + ' already exists.'
    def __repr(self):
        return self.message

class Project:
    def __init__(self, project_path, command):
        self.project_path = project_path
        self.db_session = tPipeDB.init_session(os.path.join(project_path, 'database.db'))
        #I'm going to need to take in the command, 

    def add_species(self, species_name):
        species = tPipeDB.Species(SpeciesName = species_name)
        self.db_session.add(species)
    def commit(self):
        self.db_session.commit()

    
    @staticmethod
    def createEmptyProject(project_path):
        if os.path.exists(project_path):
            raise ProjectPathAlreadyExistsError(project_path)
        else:
            os.mkdir(project_path)
            subfolders = ['FASTA', 'peptides', 'NetMHC', 'tide_indices', 'MGF', 'tide_search_results', 'percolator_results', 'misc']
            for subfolder in subfolders:
                os.mkdir(os.path.join(project_path, subfolder))
            return Project(project_path)



