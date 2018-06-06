from abc import ABC, abstractmethod, ABCMeta
from Base import Base
class AbstractEngine(Base, metaclass=ABCMeta):
    def list_search(self, mgf_name = None, index_name=None):
        pass
    def run_search(self, mgf_name, index_name, search_runner, search_name, options):
        pass
    def list_indices(self):
        pass
    def create_index(self, set_type, set_name, index_runner, index_name):
        pass
    