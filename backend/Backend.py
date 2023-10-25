from backend.CommandController import CommandController
from backend.CommandDispatcher import CommandDispatcher
from backend.QueryDispatcher import QueryDispatcher
from backend.Repo import GeomObjStorage, MultiStorage
from backend.save import saving_project_in_file, loading_project_from_file
from points.Mediator import BaseMediatorClient


class Backend(BaseMediatorClient):

    def __init__(self):
        super().__init__()
        self.storage = MultiStorage()
        self.controller = CommandController()
        self.command_create_manager = CommandDispatcher(self.storage)
        self.query_create_manager = QueryDispatcher(self.storage)

    def execute_command(self, request):  # возвращает объект Response
        new_command = self.command_create_manager.create_from(request)
        if new_command is not None:
            self.controller.push_command(new_command)
            return self.controller.do_command()  # id_list_re, id_list_dell, id_list_add = resp.unpack()
        else:
            return None

    def execute_query(self, request):
        new_command = self.query_create_manager.create_from(request)
        return new_command.do()

    def undo(self):
        self.controller.undo_command()

    def redo(self):
        return self.controller.redo_command()

    def clear(self):
        self.storage.clear()
        self.controller.clear()


""" 
backend = Backend()

# "contour": [(5, 0), (5, 1), (6, 1), (6, 0)], "holes": [[(5, 1), (6, 1), (6, 0)]]

request1 = {"type": "add", "params": {"point_list": [(1.54, -2.24), (5, 1), (6, 1), (1.54, -2.24)]}}
a = backend.execute_command(request1)
request2 = {"type": "get all", "params": {}}
b = backend.execute_query(request2)
# request3 = {"type": "convert contours to poly", "params": {"id_list": [0]}}
# d = backend.execute_command(request3)

request4 = {"type": "rotate", "params": {"id": 1, "rotation center": (1.12, 0.54), "angle": 1.22173047639603}}
# request4 = {"type": "copy", "params": {"id": 1, "vector": (1, 1)}}
e = backend.execute_command(request4)


saving_project_in_file(backend, "b_info")

new_b = loading_project_from_file("b_info")

c = 1
"""

