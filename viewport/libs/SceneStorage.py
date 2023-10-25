import math
import random
from viewport.viewport2d import viewport2dparameters as ViewportParams
from shapely.geometry import *
import copy

from backend.Repo import GeomObjStorage
from backend.Backend import Backend
from backend.Queries import GuiObg


def is_point_on_segment(segment, point, radius):
    eps = 0.0001
    if abs(segment[0][0] - segment[1][0]) > eps:
        if abs(segment[0][1] - segment[1][1]) > eps:
            k = (segment[0][1] - segment[1][1]) / (segment[0][0] - segment[1][0])
            b = segment[0][1] - k * segment[0][0]
            k_rotated = -1 / k
            b_rotated = point[1] - k_rotated * point[0]

            x_intersection = (b_rotated - b) / (k - k_rotated)
            y_intersection = x_intersection * k_rotated + b_rotated

            dist = math.sqrt((point[0] - x_intersection) ** 2 + \
                             (point[1] - y_intersection) ** 2)

            if dist <= radius:
                if (x_intersection >= min(segment[0][0], segment[1][0])) and \
                        (x_intersection <= max(segment[0][0], segment[1][0])) and \
                        (y_intersection >= min(segment[0][1], segment[1][1])) and \
                        (y_intersection <= max(segment[0][1], segment[1][1])):
                    return True
                else:
                    return False
            else:
                return False
        else:
            if (point[0] <= max(segment[0][0], segment[1][0])) and \
                    (point[0] >= min(segment[0][0], segment[1][0])):
                if (point[1] <= (max(segment[0][1], segment[1][1]) + radius)) and \
                        (point[1] >= (min(segment[0][1], segment[1][1]) - radius)):
                    return True
            else:
                return False
    else:
        if (point[1] <= max(segment[0][1], segment[1][1])) and \
                (point[1] >= min(segment[0][1], segment[1][1])):
            if (point[0] <= (max(segment[0][0], segment[1][0]) + radius)) and \
                    (point[0] >= (min(segment[0][0], segment[1][0]) - radius)):
                return True
        else:
            return False


class FrontendMediator:
    def __init__(self):
        self.ugm = None
        self.backend = Backend()

        self.connected_objects = []

        self.scene_objects = []
        self.tmp_scene_objects = []
        self.scene_properties = [ViewportParams.default_scene_properties]

    def connect_objects(self, list_of_objects):
        for element in list_of_objects:
            element.gui_mediator = self
            element.link_to_scene_properties = self.scene_properties[0]
            self.connected_objects.append(element)

    def _get_raw_data_by_id(self, id_):
        request = {"type": "get data", "params": {"id": id_}}
        return self.backend.execute_query(request)

    def _get_ids(self, id_):
        request = {"type": "get ids", "params": {}}
        return self.backend.execute_query(request)

    def reload_all(self):
        self.scene_properties[0].update({'selected_vertices': []})
        self.scene_properties[0].update({'selected_edges': []})
        # self.scene_properties[0].update({'selected_ids': []})
        self.scene_properties[0].update({'hidden_ids': []})

        request = {"type": "get all", "params": {}}
        self.scene_objects = self.backend.execute_query(request)

        for element in self.connected_objects:
            element.clear()
            for geom_obj in self.scene_objects:
                element.add_element(geom_obj)
            for geom_obj in self.tmp_scene_objects:
                element.add_tmp_element(geom_obj)

    def set_slice(self, slice_lines):
        if slice_lines is None:
            return None

        self.backend.clear()

        request = {"type": "add slice", "params": {"segment_list": slice_lines}}
        self.backend.execute_command(request)

        self.reload_all()

    def testing_add_lines(self):

        request = {"type": "add", "params": {"geom_type": "pline", "pline": [(-10, -10), (10, 10)]}}
        self.backend.execute_command(request)

        request = {"type": "add", "params": {"geom_type": "pline", "pline": [(0, 0), (-10, 10)]}}
        self.backend.execute_command(request)

        request = {"type": "add", "params": {"geom_type": "contour", "contour": [(0, 0), (-10, 10), (-10, -10), (0, 0)]}}
        self.backend.execute_command(request)

        request = {"type": "add", "params": {"geom_type": "polygon",
                                             "contour": [(-20, -20), (-20, 20), (20, 20), (20, -20), (-10, -20)],
                                             "holes": [[(-19, -19), (-17, -19), (-19, -17), (-19, -19)]]}}
        self.backend.execute_command(request)

        self.reload_all()

    def execute_command(self, input_request):
        # request = {"type": "select_by_id", "params": {"ids": selected_ids}}

        if input_request['type'] == 'add_line':
            request = {"type": "add", "params": {"point_list": input_request['params']['line_data']}}
            self.backend.execute_command(request)

            self.reload_all()

        elif input_request['type'] == 'get_selection_mode':
            return self.scene_properties[0]['selection_mode']

        elif input_request['type'] == 'select_object':
            return self.select_line(input_request['mouse_pos'])

        elif input_request['type'] == 'delete_selected_objects':
            # read selected objects
            selected_ids = self.scene_properties[0]['selected_ids']
            if len(selected_ids) == 0:
                print("Deletion list is empty")
                return None
            else:
                request = {"type": "remove", "params": {"id list": selected_ids}}
                self.backend.execute_command(request)
                self.reload_all()

        elif input_request['type'] == 'convert_selected_to_contour':
            selected_ids = self.scene_properties[0]['selected_ids']
            if len(selected_ids) == 0:
                print("Convertation list is empty")
                return None
            else:
                request = {"type": "convert poly to contours", "params": {"id": selected_ids[0]}}
                self.backend.execute_command(request)
                self.reload_all()

        elif input_request['type'] == 'copy_selected_objects':
            selected_ids = self.scene_properties[0]['selected_ids']
            if len(selected_ids) == 0:
                print("Copy list is empty")
                return None
            else:
                request = {"type": "copy", "params": {"id list": selected_ids,
                                                      "vector": (0, 0)}}
                self.backend.execute_command(request)
                self.reload_all()

        elif input_request['type'] == 'convert_selected_to_poly':
            selected_ids = self.scene_properties[0]['selected_ids']
            if len(selected_ids) == 0:
                print("Convert selected to poly list is empty")
                return None
            else:
                request = {"type": "convert contours to poly", "params": {"id list": selected_ids}}
                self.backend.execute_command(request)
                self.reload_all()

        elif input_request['type'] == 'undo':
            self.backend.undo()
            self.reload_all()

        elif input_request['type'] == 'redo':
            self.backend.redo()
            self.reload_all()

        elif input_request['type'] == 'show_vertices':
            if input_request['params']['state'] == 'hide':
                self.scene_properties[0].update({'show_vertices': False})
            elif input_request['params']['state'] == 'show':
                self.scene_properties[0].update({'show_vertices': True})
            else:
                print("Unknown show_vertices state")

        elif input_request['type'] == 'set_selection_mode':
            if input_request['params']['state'] == 'vertex':
                self.scene_properties[0].update({'selection_mode': 'vertex'})
            elif input_request['params']['state'] == 'edge':
                self.scene_properties[0].update({'selection_mode': 'edge'})
            elif input_request['params']['state'] == 'line':
                self.scene_properties[0].update({'selection_mode': 'line'})
            else:
                print("Unknown set_selection_mode state")

        elif input_request['type'] == 'move_vertex':
            selected_vertexes = self.scene_properties[0]['selected_vertices']
            mouse_pos = input_request['mouse_pos']
            # print(input_request, selected_vertexes)
            # request = {"type": "convert poly to contours", "params": {"id": selected_ids[0]}}
            request = {"type": "move point", "params": {"id": selected_vertexes[0][0],
                                                        "point ind": selected_vertexes[0][1],
                                                        "new coord": (mouse_pos[0], mouse_pos[1])}}
            self.backend.execute_command(request)

            self.reload_all()
            # return self.select_vertex(input_request['mouse_pos'])

        elif input_request['type'] == 'select_by_pos':
            selection_mode = self.scene_properties[0]['selection_mode']
            if selection_mode == 'vertex':
                return self.select_vertex(input_request['mouse_pos'])
            elif selection_mode == 'edge':
                return self.select_edge(input_request['mouse_pos'])
            elif selection_mode == 'object':
                return self.select_object(input_request['mouse_pos'])

            return None

            # return self.select_line(input_request['mouse_pos'])

        elif input_request['type'] == 'cancel_selection':
            self.scene_properties[0].update({"selected_vertices": []})
            self.scene_properties[0].update({"selected_edges": []})
            self.scene_properties[0].update({"selected_ids": []})

        elif input_request['type'] == 'set_visible_by_id':
            tmp_id = input_request['params']['id']
            hidden_ids = self.scene_properties[0]['hidden_ids']

            if input_request['params']['visible']:  # True - - set visible
                if tmp_id in hidden_ids:
                    if tmp_id in hidden_ids:
                        hidden_ids.remove(tmp_id)
                        self.scene_properties[0].update({"hidden_ids": hidden_ids})
            else:  # False - set hidden
                if tmp_id not in hidden_ids:
                    hidden_ids.append(tmp_id)
                    self.scene_properties[0].update({"hidden_ids": hidden_ids})
        elif input_request['type'] == 'rasterize':
            input_request.update({'type': 'get raster'})
            result = self.backend.execute_query(input_request)
            self.clear_tmp_objects()
            for element in result:
                element.change_properties({'color': ViewportParams.tmp_default_color})
                self.add_tmp_object(element)

        elif input_request['type'] == 'apply_raster':
            input_request.update({'type': 'raster'})
            self.clear_tmp_objects()
            """
            request = {"type": "raster", "params": {"id": input_request['params']['id'],
                                                    "slope": input_request['params']['slope']}}
                                                                """
            print(input_request)
            self.backend.execute_command(input_request)
            self.reload_all()

        elif input_request['type'] == 'make_offset':
            input_request.update({'type': 'get equidistant'})
            result = self.backend.execute_query(input_request)
            self.clear_tmp_objects()
            for element in result:
                element.change_properties({'color': ViewportParams.tmp_default_color})
                self.add_tmp_object(element)

        elif input_request['type'] == 'apply_offset':
            input_request.update({'type': 'equidistant'})
            self.clear_tmp_objects()
            self.backend.execute_command(input_request)
            self.reload_all()

    def execute_query(self, input_request):
        if input_request['type'] == 'select_by_id':
            self.scene_properties[0].update({'selected_ids': input_request['params']['ids']})
        elif input_request['type'] == 'get_data_by_id':
            request = {"type": "get data", "params": {"id": input_request['params']['id']}}
            return self.backend.execute_query(request)
        elif input_request['type'] == 'get_properties_by_id':
            request = {"type": "get dp", "params": {"id": input_request['params']['id']}}
            return self.backend.execute_query(request)

    def select_vertex(self, mouse_pos):
        grid_step = self.scene_properties[0]['camera_properties'][0]
        current_selected_vertices = self.scene_properties[0]['selected_vertices']
        hidden_ids = self.scene_properties[0]['hidden_ids']

        for element in self.scene_objects:
            if element.id not in hidden_ids:
                if (element.type == 'PLine') or (element.type == 'Contour'):
                    tmp_line = element.raw_data
                    for i in range(len(tmp_line)):
                        point = tmp_line[i]
                        dist = math.sqrt((point[0] - mouse_pos[0]) ** 2 + (point[1] - mouse_pos[1]) ** 2)
                        if dist < grid_step / 5:
                            self.scene_properties[0].update({"selected_vertices": [(element.id, i)]})
                            return 'vertex_selected'

                elif element.type == 'Polygon':
                    pass

        # add shift
        self.scene_properties[0].update({"selected_vertices": []})
        return None

    def select_edge(self, mouse_pos):
        grid_step = self.scene_properties[0]['camera_properties'][0]
        current_selected_vertices = self.scene_properties[0]['selected_vertices']
        hidden_ids = self.scene_properties[0]['hidden_ids']

        for element in self.scene_objects:
            if element.id not in hidden_ids:
                if (element.type == 'PLine') or (element.type == 'Contour'):
                    tmp_line = element.raw_data
                    for i in range(len(tmp_line)-1):
                        edge = (tmp_line[i], tmp_line[i+1])
                        if is_point_on_segment(edge, (mouse_pos[0], mouse_pos[1]), grid_step / 10):
                            self.scene_properties[0].update({"selected_edges": [[element.id, i]]})
                            return 'edge_selected'

                elif element.type == 'Polygon':
                    pass

        # add shift
        self.scene_properties[0].update({"selected_edges": []})
        return None

    def select_object(self, mouse_pos):
        grid_step = self.scene_properties[0]['camera_properties'][0]
        current_selected_ids = self.scene_properties[0]['selected_ids']
        hidden_ids = self.scene_properties[0]['hidden_ids']

        for element in self.scene_objects:
            if element.id not in hidden_ids:
                if (element.type == 'PLine') or (element.type == 'Contour'):
                    tmp_line = element.raw_data
                    for i in range(len(tmp_line)-1):
                        edge = (tmp_line[i], tmp_line[i+1])
                        if is_point_on_segment(edge, (mouse_pos[0], mouse_pos[1]), grid_step / 10):
                            self.scene_properties[0].update({"selected_ids": [element.id]})
                            return 'object_selected'

                elif element.type == 'Polygon':
                    pass

        # add shift
        self.scene_properties[0].update({"selected_edges": []})
        return None

    def add_tmp_object(self, data):
        for element in self.connected_objects:
            element.add_tmp_element(data)

    def clear_tmp_objects(self):
        for element in self.connected_objects:
            element.clear_tmp_elements()


# class SceneStorage:
#     def __init__(self):
#         self.mediator = None
#
#         self.scene_objects = []  # Can access to data by id from self.objects_params
#         self.scene_properties = [ViewportParams.default_scene_properties]  # list of ...
#         self.id_numeration_counter = 0
#
#         self.raw_data = []
#         self.last_changes = []
#
#     def init(self):
#         self.mediator.notify(self, ['set_main_storage'])  # configure pointer to this storage
#
#     def get_all_data(self):
#         scene_objects_copy = copy.deepcopy(self.scene_objects)
#         scene_properties_copy = copy.deepcopy(self.scene_properties)
#         return scene_objects_copy, scene_properties_copy
#
#     def get_line_data_by_id(self, line_id):
#         for element in self.scene_objects:
#             if element[0] == line_id:
#                 element_copy = copy.deepcopy(element[1])
#                 return element_copy
#         return None
#
#     def add_lines(self, source, lines_data_list):
#         # request = {"type": "add", "params": {"geom_type": "pline", "pline": lines_data_list[0][1][0]}}
#         request = {"type": "add", "params": {"geom_type": "pline", "pline": lines_data_list[0][1][0]}}
#
#         add_result = self.facade.add_pline_to_slice(lines_data_list[0][1][0])
#         # add_result = self.facade.send_to_backend(request)
#         return add_result
#
#     def set_slice(self, slice_lines):
#         self.scene_objects.clear()
#         self.raw_data.clear()
#
#         self.facade.clear()
#
#         if slice_lines is None:
#             self.mediator.notify(self, ['upload_all_data_from_storage'])
#             return None
#
#         request = {"type": "add slice", "params": {"segment list": slice_lines}}
#         self.facade.send_to_backend(request)
#         # new_id_list = self.facade.add_slice(slice_lines)
#         ids = self.facade.get_all_ids()
#         plines = self.facade.get_plines()
#
#         for i in range(len(plines)):
#             element = plines[i]
#             element_properties = ViewportParams.default_line_properties.copy()
#
#             if 'name' not in element_properties.keys():
#                 element_properties.update({'name': "line_" + str(ids[i])})
#
#             if element[0] == element[-1]:
#                 element_properties.update({'type': "contour"})
#             else:
#                 element_properties.update({'type': "line"})
#
#             self.scene_objects.append([ids[i], [element, element_properties]])
#             self.raw_data.append(element)
#             self.id_numeration_counter += 1
#
#         self.mediator.notify(self, ['upload_all_data_from_storage'])
#
#     def set_selected_lines(self, line_nums):
#         self.scene_properties[0].update({"selected_lines": [line_nums]})
#         #  Update selection in TAB-widget
#         self.mediator.notify(self, ['upload_tab_selection_from_storage'])
#
#     def restore_data_from_storage(self):
#         self.scene_objects.clear()
#         self.raw_data.clear()
#
#         ids = self.facade.get_all_ids()
#         plines = self.facade.get_plines()
#         # plines = self.facade.get_plines(ids)
#
#         for i in range(len(plines)):
#             element = plines[i]
#             element_properties = ViewportParams.default_line_properties.copy()
#
#             if 'name' not in element_properties.keys():
#                 element_properties.update({'name': "line_" + str(ids[i])})
#
#             if element[0] == element[-1]:
#                 element_properties.update({'type': "contour"})
#             else:
#                 element_properties.update({'type': "line"})
#             # print(element_properties)
#
#             self.scene_objects.append([ids[i], [element, element_properties]])
#             self.raw_data.append(element)
#             self.id_numeration_counter += 1
#
#         self.mediator.notify(self, ['upload_all_data_from_storage'])
#
#     def move_vertex(self, change_info):
#         id_ = change_info[0]
#         point_ind = change_info[1]
#         new_coord = (change_info[2][0], change_info[2][1])
#         request = {"type": "move point", "params": {"id": id_, "point ind": point_ind, "new coord": new_coord}}
#         # request = {"type": "move point", "params": {"id": id_, "point id": point_ind, "new coord": new_coord}}
#         movement_result = self.facade.send_to_backend(request)
#         return movement_result
#
#     def change_properties(self, changes_list):
#         self.last_changes = ['change_properties', []]
#         for element in self.scene_objects:
#             for changing_element in changes_list:
#                 if element[0] == changing_element[0]:  # compare i
#                     element[1][1].update(changing_element[1][1])
#                     self.last_changes[1].append([element[0], [None, changing_element[1][1]]])
#                     break
#         # Add warning if ID is not enough!!!
#
#     def delete_selected_lines(self):
#         selected_lines = self.scene_properties[0]["selected_lines"]
#
#         id_ = selected_lines[0]
#
#         request = {"type": "remove", "params": {"id": id_}}
#         delete_result = self.facade.send_to_backend(request)
#
#         return delete_result
#
#     def get_last_changes(self):
#         return self.last_changes
#
#     def add_offset_line(self, id_offset):
#         # self.last_changes = ['add_lines', []]
#         for i in range(len(self.scene_objects)):
#             if self.scene_objects[i][0] == id_offset[0]:
#                 contour = self.scene_objects[i][1][0]
#                 contour = LinearRing(contour)
#                 contour_offset = contour.parallel_offset(3.5, side='left', resolution=16, join_style=1, mitre_limit=1.0)
#
#                 upload_data = []
#
#                 if contour_offset.geom_type == 'LineString':
#                     contour_offset = list(contour_offset.coords)
#                     tmp_list = []
#                     for point in contour_offset:
#                         tmp_list.append([point[0], point[1]])
#                     upload_data.append([0, [tmp_list, {'visible': True,
#                                                        'reverse': False,
#                                                        'selected': True,
#                                                        'width': ViewportParams.line_default_width,
#                                                        'color': ViewportParams.line_default_color}]])
#
#                 elif contour_offset.geom_type == 'MultiLineString':
#                     for line in contour_offset:
#                         line_as_list = list(line.coords)
#                         tmp_list = []
#                         for point in line_as_list:
#                             tmp_list.append([point[0], point[1]])
#                         upload_data.append([0, [tmp_list, {'visible': True,
#                                                            'reverse': False,
#                                                            'selected': True,
#                                                            'width': ViewportParams.line_default_width,
#                                                            'color': ViewportParams.line_default_color}]])
#                 else:
#                     pass
#                 self.add_lines(self, upload_data)
#
#     def set_scene_properties(self, new_properties):
#         keys_list = new_properties.keys()
#         self.scene_properties[0].update(new_properties)
#
#     def get_scene_properties(self):
#         return self.scene_properties[0]
#
#     def set_selected_objects(self, id_list):
#         self.scene_properties[0].update({"selected_lines": id_list})
#
#     def select_vertices(self, x_pos, y_pos):
#         grid_step = self.scene_properties[0]['camera_properties'][0]
#         current_selected_vertices = self.scene_properties[0]['selected_vertices']
#         for element in self.scene_objects:
#             if element[1][1]['visible']:
#                 for i in range(len(element[1][0])):
#                     point = element[1][0][i]
#                     dist = math.sqrt((point[0] - x_pos) ** 2 + (point[1] - y_pos) ** 2)
#                     if dist < grid_step / 5:
#                         self.scene_properties[0].update({"selected_vertices": [(element[0], i)]})
#                         return 'vertex_selected'
#         self.scene_properties[0].update({"selected_vertices": []})
#         return None
#
#     def select_edge(self, x_pos, y_pos):
#         for element in self.scene_objects:
#             if element[1][1]['visible']:
#                 for i in range(len(element[1][0]) - 1):
#                     segment = (element[1][0][i], element[1][0][i + 1])
#                     if is_point_on_segment(segment, (x_pos, y_pos),
#                                            self.scene_properties[0]['camera_properties'][0] / 10):
#                         self.scene_properties[0].update({"selected_edges": [[element[0], i]]})
#                         return 'edge_selected'
#         self.scene_properties[0].update({"selected_edges": []})
#         return None
#
#     def select_line(self, x_pos, y_pos):
#         for element in self.scene_objects:
#             if element[1][1]['visible']:
#                 for i in range(len(element[1][0]) - 1):
#                     segment = (element[1][0][i], element[1][0][i + 1])
#                     if is_point_on_segment(segment, (x_pos, y_pos),
#                                            self.scene_properties[0]['camera_properties'][0] / 10):
#                         self.set_selected_lines(element[0])
#                         return 'line_selected'
#         self.scene_properties[0].update({"selected_lines": []})
#         return None
#
#     def delete_selected_vertices(self):
#         selected_vertices = self.scene_properties[0]["selected_vertices"]
#         self.scene_properties[0].update({"selected_vertices": []})
#
#         id_ = selected_vertices[0][0]
#         point_ind = selected_vertices[0][1]
#
#         request = {"type": "remove point", "params": {"id": id_, "point ind": point_ind}}
#         # request = {"type": "remove point from slice", "params": {"id": id_, "point id": point_ind}}
#         delete_result = self.facade.send_to_backend(request)
#
#         return delete_result
#
#     def add_median_point(self):
#         selected_edges = self.scene_properties[0]["selected_edges"]
#         self.scene_properties[0].update({"selected_edges": []})
#
#         id_ = selected_edges[0][0]
#         prev_ind = selected_edges[0][1]
#
#         # request = {"type": "add point", "params": {"id": id_, "prev ind": prev_ind}}
#         request = {"type": "add point", "params": {"id": id_, "point id1": prev_ind, "point id2": prev_ind+1}}
#         add_result = self.facade.send_to_backend(request)
#
#         return add_result
#
#     def add_offset_line(self):
#         selected_lines = self.scene_properties[0]["selected_lines"]
#         id_ = selected_lines[0]
#         dist = -3.0  # поменять
#
#         request = {"type": "get equidistant", "params": {"id": id_, "distance": dist}}
#         add_result = self.facade.send_to_backend(request)
#
#         return add_result
#
#     def cancel_selection(self):
#         self.scene_properties[0].update({"selected_vertices": []})
#         self.scene_properties[0].update({"selected_edges": []})
#         self.scene_properties[0].update({"selected_lines": []})
#
#     def clear(self):
#         self.objects.clear()  # Can access to data by id from self.objects_params
#         self.selected_objects_id_list.clear()  # list for light up in viewport and tabl
#         return 1
#
#     def receive_command(self, msg):
#         if msg[0] == 'select_vertex':
#             return self.select_vertices(msg[1], msg[2])
#
#         if msg[0] == 'select_edge':
#             return self.select_edge(msg[1], msg[2])
#
#         if msg[0] == 'select_line':
#             return self.select_line(msg[1], msg[2])
#
#         if msg[0] == 'cancel_selection':
#             self.cancel_selection()
#
#         if msg[0] == 'selection_mode':
#             return self.scene_properties[0]['selection_mode']
#
#         if msg[0] == 'delete_selected_vertex':
#             result = self.delete_selected_vertices()
#             self.restore_data_from_storage()
#             return result
#
#         if msg[0] == 'add_median_point':
#             result = self.add_median_point()
#             self.restore_data_from_storage()
#             return result
#
#         if msg[0] == 'add_offset_line':
#             result = self.add_offset_line()
#             self.restore_data_from_storage()
#             return result
#
#
# class StorageTab:
#     def __init__(self, parent):
#         self.parent = parent
#         self.mediator = None
#         self.main_storage = None
#
#         self.scene_objects = []
#         self.scene_properties = []
#
#         self.link_to_scene_properties = []
#
#     def set_main_storage(self, main_storage):
#         self.main_storage = main_storage
#         self.link_to_scene_properties = main_storage.scene_properties[0]
#
#     def upload_all_data_from_ms(self):
#         self.scene_objects, self.scene_properties = self.main_storage.get_all_data()
#         self.parent.update_from_storage("upload_all")
#
#     def change_objects_properties(self, changes_objects_list):
#         self.mediator.notify(self, ['change_objects_properties', changes_objects_list])
#
#     def delete_objects(self, id_list):
#         self.mediator.notify(self, ['delete_objects', id_list])
#
#     def add_offset_line(self, selected_objects_id_list):
#         if len(selected_objects_id_list) == 1:
#             self.mediator.notify(self, ['add_offset_line', selected_objects_id_list])
#
#     def set_selected_objects(self, id_list):
#         self.main_storage.set_selected_objects(id_list)
#
#     def get_scene_properties(self):
#         return self.main_storage.get_scene_properties()
#
#     def update_selected_lines(self):
#         selected_lines = self.main_storage.scene_properties[0]["selected_lines"]
#         self.parent.set_lines_selection(selected_lines)
#
#
# class StorageViewport:
#     def __init__(self, parent):
#         self.parent = parent
#         self.mediator = None
#         self.main_storage = None
#
#         self.scene_objects = []
#         self.scene_properties = []
#
#         self.link_to_scene_properties = []
#
#     def set_main_storage(self, main_storage):
#         self.main_storage = main_storage
#         self.link_to_scene_properties = main_storage.scene_properties[0]
#
#     def upload_all_data_from_ms(self):
#         self.scene_objects, self.scene_properties = self.main_storage.get_all_data()
#         self.parent.update_from_storage(["upload_all"])
#
#     def add_line(self, line):
#         self.mediator.notify(self, ['add_lines', [line]])
#
#     def move_vertex(self, line_id, vertex_num, new_position):
#         self.mediator.notify(self, ['move_vertex', [line_id, vertex_num, new_position]])
#
#     def add_line_in_viewport(self):
#         line = [[random.random() * 10 - 5, random.random() * 10 - 5],
#                 [random.random() * 10 - 5, random.random() * 10 - 5],
#                 [random.random() * 10 - 5, random.random() * 10 - 5]]
#
#         self.mediator.notify(self, ['add_lines', [line]])
#
#     def get_last_changes_from_storage(self, storage):
#         last_changes = storage.get_last_changes()
#
#         if last_changes[0] == 'add_lines':
#             list_for_bind = []
#
#             for element in last_changes[1]:
#                 list_for_bind.append(len(self.scene_objects))
#                 self.scene_objects.append(element.copy())
#
#             self.parent.update_from_storage(["bind_lines", list_for_bind])  # Add line to GPU
#
#         elif last_changes[0] == 'change_properties':
#             for element in self.scene_objects:
#                 for changing_element in last_changes[1]:
#                     if element[0] == changing_element[0]:  # compare id
#                         element[1][1].update(changing_element[1][1])
#
#         elif last_changes[0] == 'delete_objects':
#             num_elements_for_delete = []
#             for i in range(len(self.scene_objects)):
#                 if self.scene_objects[i][0] in last_changes[1]:
#                     num_elements_for_delete.append(i)
#
#             if num_elements_for_delete is []:
#                 return None
#             num_elements_for_delete.reverse()
#
#             self.parent.update_from_storage(["unbind", num_elements_for_delete])
#
#             for num_element in num_elements_for_delete:
#                 del self.scene_objects[num_element]
#
#         elif last_changes[0] == 'update_data':
#             list_for_rebind = last_changes[1]
#             self.parent.update_from_storage(["rebind_lines", list_for_rebind])  # Reload lines in GPU
#             # for element in last_changes[1]:
#             #     list_for_bind.append(len(self.scene_objects))
#             #     self.scene_objects.append(element.copy())
#             #
#             # self.parent.update_from_storage(["bind_lines", list_for_bind])  # Add line to GPU
#
#     def get_scene_properties(self):
#         return self.main_storage.get_scene_properties()
#
#     def select_vertices(self, x_pos, y_pos):
#         self.main_storage.select_vertices(x_pos, y_pos)
#
#     def get_line_data_by_id(self, line_id):
#         # self.main_storage.get_line_data_by_id(line_id[0])
#         return self.main_storage.get_line_data_by_id(line_id)
#
#
# class StorageMediator:
#     def __init__(self, scene_storage, tab_storage, viewport_storage):
#         self.scene_storage = scene_storage  # main storage
#         self.scene_storage.mediator = self
#
#         self.tab_storage = tab_storage
#         self.tab_storage.mediator = self
#
#         self.viewport_storage = viewport_storage
#         self.viewport_storage.mediator = self
#
#     def notify(self, sender: object, event):
#         if event[0] == 'set_main_storage':
#             self.viewport_storage.set_main_storage(sender)
#             self.tab_storage.set_main_storage(sender)
#             return 1
#
#         if event[0] == 'upload_all_data_from_storage':
#             self.viewport_storage.upload_all_data_from_ms()
#             self.tab_storage.upload_all_data_from_ms()
#             return 1
#
#         if event[0] == 'add_lines':
#             if sender == self.viewport_storage:
#                 list_for_upload = []
#                 for line in event[1]:
#                     list_for_upload.append([0,  # id is zero = not id line
#                                             [line,  # line data
#                                              ViewportParams.default_line_properties.copy()]])  # line properties
#                 self.scene_storage.add_lines(sender, list_for_upload)
#
#                 self.scene_storage.restore_data_from_storage()
#             elif sender == self.tab_storage:
#                 print("Uploaded lines from TAB widget is not supported")
#                 return None
#
#         if event[0] == 'change_objects_properties':
#             if sender == self.tab_storage:
#                 self.scene_storage.change_properties(event[1])
#                 self.viewport_storage.get_last_changes_from_storage(self.scene_storage)
#                 self.tab_storage.upload_all_data_from_ms()
#             elif sender == self.viewport_storage:
#                 print("Changing properties from VP widget is not supported yet")
#                 return None
#
#         if event[0] == 'delete_objects':
#             if sender == self.tab_storage:
#                 self.scene_storage.delete_selected_lines()
#                 self.scene_storage.restore_data_from_storage()
#                 # self.viewport_storage.get_last_changes_from_storage(self.scene_storage)
#                 # self.tab_storage.upload_all_data_from_ms()
#
#         if event[0] == 'add_offset_line':
#             self.scene_storage.add_offset_line(event[1])
#             # !!!!
#             self.viewport_storage.get_last_changes_from_storage(self.scene_storage)
#             self.tab_storage.upload_all_data_from_ms()
#
#         if event[0] == 'move_vertex':
#             self.scene_storage.move_vertex(event[1])
#
#             self.scene_storage.restore_data_from_storage()
#
#         if event[0] == 'upload_tab_selection_from_storage':
#             self.tab_storage.update_selected_lines()
#
#
# class MainWindow:
#     def __init__(self):
#         self.storage = SceneStorage()
#         self.storage_tab = StorageTab(self)
#         self.storage_vp = StorageViewport(self)
#
#         self.storage_mediator = StorageMediator(self.storage,
#                                                 self.storage_tab,
#                                                 self.storage_vp)
#
#         line1 = [[random.random() * 10 - 5, random.random() * 10 - 5],
#                  [random.random() * 10 - 5, random.random() * 10 - 5],
#                  [random.random() * 10 - 5, random.random() * 10 - 5]]
#
#         line2 = [[random.random() * 10 - 5, random.random() * 10 - 5],
#                  [random.random() * 10 - 5, random.random() * 10 - 5],
#                  [random.random() * 10 - 5, random.random() * 10 - 5]]
#
#         line3 = [[random.random() * 10 - 5, random.random() * 10 - 5],
#                  [random.random() * 10 - 5, random.random() * 10 - 5],
#                  [random.random() * 10 - 5, random.random() * 10 - 5]]
#
#         self.storage.set_initial_data([[line1, ViewportParams.default_line_properties.copy()],
#                                        [line2, ViewportParams.default_line_properties.copy()],
#                                        [line3, ViewportParams.default_line_properties.copy()]])
#
#         self.storage_vp.add_line_in_viewport()
#         self.storage_vp.add_line_in_viewport()
#         self.storage_vp.add_line_in_viewport()
#
#         self.storage_tab.change_objects_properties([[2, [None,
#                                                          {'visible': False}]]])
#
#         self.storage_tab.delete_objects([1, 4])
#
#         print("---Main----")
#         for el in self.storage.scene_objects:
#             print(el[0], el[1][1])
#         print("---VP----")
#         for el in self.storage_vp.scene_objects:
#             print(el[0], el[1][1])
#         print("---TAB----")
#         for el in self.storage_tab.scene_objects:
#             print(el[0], el[1][1])
#
#     def update_from_storage(self, msg):
#         pass
#
# # mw = MainWindow()
