import tPipeDB
import os

class Error(Exception):
    pass

class ProjectPathAlreadyExistsError(Error):
    def __init__(self, project_folder):
        self.message = 'Project folder ' + project_folder + ' already exists.'
    def __repr(self):
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

class Project:
    def __init__(self, project_path, command):
        self.project_path = project_path
        self.db_session = tPipeDB.init_session(os.path.join(project_path, 'database.db'))
        self.command = tPipeDB.Command(commandString = command)
        self.db_session.add(self.command)
        self.db_session.commit()

    def add_species(self, species_name):
        species = tPipeDB.Species(SpeciesName = species_name)
        self.db_session.add(species)
    def commit(self):
        self.command.executionSuccess = 1
        
        self.db_session.commit()

    def get_commands(self):
        commands = []
        for row in self.db_session.query(tPipeDB.Command):
            commands.append(row)
        return commands
    def get_species(self):
        species = []
        for row in self.db_session.query(tPipeDB.Species):
            hla = []
            for hla_row in row.hlas:
                hla.append(hla_row.HLAName)
            
            species.append({'id': row.idSpecies, 'name': row.SpeciesName, 'hla':hla  })
        return species

    def list_hla(self, species_name=None, species_id=None):
        if species_name:
            species_row = self.db_session.query(tPipeDB.Species).filter_by(SpeciesName=species_name).first()
            if species_row:
                species_id = species_row.idSpecies
            else:
                raise NoSuchSpeciesError(species_name)
        query = self.db_session.query(tPipeDB.HLA)
        if species_id:
            query = query.filter_by(species_id=species_id)
        rows = query.all()
        hlas = []
        for row in rows:
            hla = {'name': row.HLAName, 'id': str(row.idHLA)}
            if row.species:
                hla['species_id'] = str(row.species.idSpecies)
                hla['species_name'] = row.species.SpeciesName
            else:
                hla['species_id'] = 'None'
                hla['species_name'] = 'None'
            hlas.append(hla)
        return hlas
    def add_hla(self, hla_name, species, speciesIsID):
        species_rows = []
        if speciesIsID:
            species_rows = self.db_session.query(tPipeDB.Species).filter_by(idSpecies=species).all()
            if len(species_rows) == 0:
                raise NoSpeciesWithIDError(species)
            elif len(species_rows) > 1:
                raise MultipleSpeciesWithSameIDError(species)
        else:        
            species_rows = self.db_session.query(tPipeDB.Species).filter_by(SpeciesName=species).all()
            print(species_rows)
            print(len(species_rows))
            if len(species_rows) > 1:
                raise MultipleSpeciesWithSameNameError(species)
            elif len(species_rows) == 0:
                raise NoSpeciesWithNameError(species)
        hla_rows = self.db_session.query(tPipeDB.HLA).filter_by(HLAName = hla_name).all()
        if len(hla_rows) > 0:
            raise HLAWithNameExistsError(hla_name)
        hla = tPipeDB.HLA(HLAName = hla_name, species_id = species_rows[0].idSpecies)
        self.db_session.add(hla)
        self.db_session.commit()
        return hla.idHLA

        
        
        
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



