import copy
from viewport.libs.WAAMmodel import WAAMmodel
from PyQt6.QtGui import QMatrix4x4


class ProjectMediator:
    def __init__(self):
        self.ugm = None
        self.connected_objects = []

        self.models = []
        self.cs_plane_transform_mat = QMatrix4x4()
        self.cs_plane_transform_mat.setToIdentity()

    def connect_objects(self, list_of_objects):
        for element in list_of_objects:
            element.mediator = self
            self.connected_objects.append(element)

    def execute_command(self, input_request):
        if input_request['type'] == 'add_model':
            filename = input_request['params']['file_name']
            waam_model = WAAMmodel(filename, scale=1)

            for element in self.connected_objects:
                element.add_object(waam_model)

            for element in self.connected_objects:
                element.execute_command({"type": "set_model_range", "params": {"range": waam_model.model_size_rank}})

            self.models.append(waam_model)

            # ADD "MAKE SLICE"

        if input_request['type'] == 'set_active_object_transform_mat':
            command = {"type": "set_transform_mat", "params": {"transform_mat": input_request['params']['transform_mat']}}
            # self.parent.project_mediator.execute_command(request)
            for element in self.connected_objects:
                element.execute_command(command)

        if input_request['type'] == 'set_cs_plane_transform_mat':
            self.cs_plane_transform_mat = input_request['params']['transform_mat']
            cs_transform_mat_inverted = copy.copy(self.cs_plane_transform_mat)
            cs_transform_mat_inverted = cs_transform_mat_inverted.inverted()[0]
            tmp = cs_transform_mat_inverted * self.models[-1].model_transform_mat
            slice_lines = self.models[-1].make_slice(tmp)

            self.ugm.execute_command({"type": "make_slice", "params": {"lines": slice_lines}})

    def execute_request(self, request):
        if request['type'] == 'get_cs_plane_transform_mat':
            return self.cs_plane_transform_mat


