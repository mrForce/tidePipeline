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
    def __init__(self, project_path):
        self.project_path = project_path
        self.db_session = tPipeDB.init_session(os.path.join(project_path, 'database.db'))

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
            

