from copy import deepcopy
from collections import namedtuple
from dataclasses import dataclass
from stl import mesh
from mesh_slicer import SimpleStorage

# только для демонстрации возможностей архитектуры гуя
# в прод ни ногой
def importSTL(filename):

    pass

class minicommand:
    def __init__(self, storage:SimpleStorage):
        self._storage = storage

    def do(self):
        pass

class import_mesh_minicommand(minicommand):
    def __init__(self, storage, filename):
        super().__init__(storage)
        self._id = None
        self._filename = filename

    def do(self):
        m = mesh.Mesh.from_file(filename)
        self._id = self._storage.add_value
        return self._id

    def undo(self):
        self._storage.pop(self._id)

# по колхозному сделана отмена
class pop_mesh_minicommand(minicommand):
    def __init__(self, storage, id_):
        super().__init__(storage)
        self._id = id_
        self._mesh_backup = None

    def do(self):
        self._mesh_backup = self._storage.pop(self._id)
        return self._storage.pop(id_, False)

    def undo(self):
        self._storage.add_value({id_: self._mesh_backup})


# redo не будет
class command_parser:
    def __init__(self, storage: SimpleStorage):
        self._storage = storage

    def parse(self, d:dict):
        type = d["type"]
        if type == "IMPORT_MESH":
            filename = d["filename"]
            return import_mesh_minicommand(self._storage, filename)
        elif type == "POP_MESH":
            id_ = d["id"]
            return pop_mesh_minicommand(self._storage, id_)
        return None






class minibackend:
    def __init__(self):
        self._storage = SimpleStorage()
        self._command_parser = command_parser(self._storage)
        self._command_queue = []


    def add_mesh(self, mesh, CS = WCS):
        new_id = self._last_id + 1
        self._last_id += 1
        self._storage.update[id] =

    def execute_command(self, command):
        pass

    def execute_request(self, request):
        pass


