from copy import deepcopy, copy

from backend.GeomObject import GeomObject
from backend.Repo import MultiStorage
from backend.Specifications import equidistant_spec, add_to_group_spec, group_disband_spec, new_group_spec, cut_spec, \
    raster_spec, remove_collinear_spec, convert_poly_to_contours_spec, convert_contours_to_poly_spec, \
    remove_point_from_nonlinear_spec, add_point_to_nonlinear_spec, pline_cut_poly_spec, copy_spec, sceleton_spec, \
    move_point_dcel_spec
from backend.commands.RepoCommands import iCommand, Response
from base.geom.algo.DCELedit import move_point_at_dcel
from base.geom.algo.GroupAlgo import create_new_group, disband_group, add_objects_to_list
from base.geom.algo.algo import copy_geoms, get_cut_lines
from base.geom.algo.buffer import serial_buffer
from base.geom.algo.convert import convert_contours_to_poly, convert_poly_to_contours
from base.geom.algo.cut import cut_poly_with_pline, cut
from base.geom.algo.geom_editing import add_point_to_graph, rem_point_from_graph
from base.geom.algo.RemoveCollinear import remove_collinear
from base.geom.algo.skeleton import gg_skeleton
from base.geom.primitives.dcel import DCEL
from base.geom.primitives.geomgraph import GeomGraph
from base.geom.primitives.linear import Contour, PLine, Polygon


class ApplyAlgCommand(iCommand):
    __slots__ = ["_input_ids", "_algo", "__delete_old",
                 "__output_ids", "_input_geom_list", "__output_geom_list", "__is_complete"]

    def __init__(self, storage: MultiStorage, input_id_list: list, algo, delete_old=False, create_group=False):
        super().__init__(storage)
        self._input_ids = deepcopy(input_id_list)  # в конструкторах-наследниках будет сообщать доп параметры
        self._algo = algo
        self.__delete_old = delete_old
        self.__output_ids = []
        self._input_geom_list = []
        self.__output_geom_list = []
        self.__is_complete = False

    def _call_algo(self, input_geom_list):
        return []

    def do(self):
        self._input_geom_list = [self._storage[input_id].geom for input_id in self._input_ids]
        self.__output_geom_list = deepcopy(self._call_algo(self._input_geom_list))
        self.__output_ids = [self._storage.add_geomobject(GeomObject(geom)) for geom in self.__output_geom_list]
        self.__is_complete = True
        if self.__delete_old and self.__output_ids:
            for id_ in self._input_ids:
                self._storage.rem_obj(id_)
            return Response(id_list_add=self.__output_ids, id_list_delete=self._input_ids)
        else:
            return Response(id_list_add=self.__output_ids)

    def _validate(self):
        self._specification.deep_validation({"id_list": self._storage.get_primitive_list_by_id(self._input_geom_list)})

    def undo(self):
        # self._storage.remove_from_group_list(self.__group_names, self.__output_ids)
        for id_ in self.__output_ids:
            self._storage.rem_obj(id_)
        self.__is_complete = False
        if self.__delete_old:  # если удаляли - вернуть
            for id_ in self._input_ids:
                self._storage.add_from_archive(id_)
            # self._storage.extend_group_list(self.__group_names, self.__input_ids)
            return Response(id_list_delete=self.__output_ids, id_list_add=self._input_ids)
        else:
            return Response(id_list_delete=self.__output_ids)

    def redo(self):
        for id_ in self.__output_ids:
            self._storage.add_from_archive(id_)
        self.__is_complete = True
        if self.__delete_old:  # если удаляли - тоже удалить
            for id_ in self._input_ids:
                self._storage.rem_obj(id_)
            return Response(id_list_add=self.__output_ids, id_list_delete=self._input_ids)
        else:
            return Response(id_list_add=self.__output_ids)

    def __del__(self):
        if not self.__is_complete:
            list(map(lambda id: self._storage.delete(id), self.__output_ids))
        elif self.__is_complete:
            list(map(lambda id: self._storage.delete(id), self._input_ids))


class Skeletonize(ApplyAlgCommand):
    __slots__ = ["_need_clipping"]

    def __init__(self, storage: MultiStorage, input_geom_id_list, clipping=False):
        super().__init__(storage, input_id_list=input_geom_id_list, algo=gg_skeleton, delete_old=False)
        self._specification = sceleton_spec
        self._need_clipping = clipping

    def _call_algo(self, input_geom_list):
        self._validate()
        #  на вход подаётся спсиок полигонов
        return self._algo(input_geom_list, self._need_clipping)


class Copy(ApplyAlgCommand):
    __slots__ = ["_vector"]

    def __init__(self, storage: MultiStorage, input_geom_id_list, vec: tuple):
        super().__init__(storage, input_id_list=input_geom_id_list, algo=copy_geoms, delete_old=False)
        self._specification = copy_spec
        self._vector = vec

    def _call_algo(self, input_geom_list):
        self._validate()
        return self._algo(input_geom_list, copy(self._vector))


class ConvertContoursToPoly(ApplyAlgCommand):
    def __init__(self, storage: MultiStorage, contour_id_list):
        super().__init__(storage, input_id_list=contour_id_list, algo=convert_contours_to_poly, delete_old=True)
        self._specification = convert_contours_to_poly_spec

    def _call_algo(self, input_geom_list):
        self._validate()
        return self._algo(input_geom_list)


class CutPolyWithPline(ApplyAlgCommand):
    __slots__ = "_segment_list"

    def __init__(self, storage: MultiStorage, pline_id, polygon_id):
        super().__init__(storage, input_id_list=[pline_id, polygon_id], algo=cut_poly_with_pline, delete_old=True)
        self._specification = pline_cut_poly_spec

    def _call_algo(self, input_geom_list):
        self._validate()
        return self._algo(input_geom_list)

    def _validate(self):
        self._specification.deep_validation(
            {"pline_id": self._storage.get_primitive_list_by_id(self._input_geom_list[0]),
             "poly_id": self._storage.get_primitive_list_by_id(self._input_geom_list[1])})


class AddPointToEdgeCenterGraph(ApplyAlgCommand):
    __slots__ = ["__id1", "__id2"]

    def __init__(self, storage: MultiStorage, input_geom_id: int, id1: int, id2: int):
        super().__init__(storage, input_id_list=[input_geom_id], algo=add_point_to_graph, delete_old=True)
        self._specification = add_point_to_nonlinear_spec
        self.__id1 = id1
        self.__id2 = id2

    def _call_algo(self, input_geom_list):
        self._validate()
        return self._algo(input_geom_list[0], self.__id1, self.__id2)

    def _validate(self):
        self._specification.deep_validation(
            {"geom_id": self._storage.get_primitive_list_by_id(self._input_geom_list[0])})


class RemPointFromGraph(ApplyAlgCommand):
    __slots__ = "__point_id"

    def __init__(self, storage: MultiStorage, input_geom_id: int, id_: int):
        super().__init__(storage, input_id_list=[input_geom_id], algo=rem_point_from_graph, delete_old=True)
        self._specification = remove_point_from_nonlinear_spec
        self.__point_id = id_

    def _call_algo(self, input_geom_list):
        self._validate()
        return self._algo(input_geom_list[0], self.__point_id)

    def _validate(self):
        self._specification.deep_validation(
            {"geom_id": self._storage.get_primitive_list_by_id(self._input_geom_list[0])})


class MovePointDCEL(ApplyAlgCommand):
    __slots__ = ["__point_id", "_new_point_coord", "_old_geom"]

    def __init__(self, storage: MultiStorage, input_geom_id: int,  point_id: int, new_coord: tuple):
        super().__init__(storage, input_id_list=[input_geom_id], algo=move_point_at_dcel, delete_old=True)
        self._specification = move_point_dcel_spec
        self.__point_id = point_id
        self._new_point_coord = new_coord

    def _call_algo(self, input_geom_list):
        self._validate()
        return self._algo(input_geom_list[0], self.__point_id, self._new_point_coord)

    def _validate(self):
        self._specification.deep_validation(
            {"dcel_id": self._storage.get_primitive_list_by_id(self._input_geom_list[0])})


class ConvertPolyToContours(ApplyAlgCommand):

    def __init__(self, storage: MultiStorage, polygon_id):
        super().__init__(storage, input_id_list=[polygon_id], algo=convert_poly_to_contours, delete_old=True)
        self._specification = convert_poly_to_contours_spec

    def _call_algo(self, input_geom_list):
        self._validate()
        return self._algo(input_geom_list)

    def _validate(self):
        self._specification.deep_validation(
            {"poly_id": self._storage.get_primitive_list_by_id(self._input_geom_list[0])})


class RemoveCollinear(ApplyAlgCommand):

    def __init__(self, storage: MultiStorage, input_geom_id, delete_old):
        super().__init__(storage, [input_geom_id], algo=remove_collinear, delete_old=delete_old)
        self._specification = remove_collinear_spec

    def _call_algo(self, input_geom_list=None):
        self._validate()
        return [self._algo(input_geom_list[0])]

    def _validate(self):
        self._specification.deep_validation(
            {"geom_id": self._storage.get_primitive_list_by_id(self._input_geom_list[0])})


class AddRaster(ApplyAlgCommand):
    __slots__ = ["_slope_k", "_bead_width", "_initial_indent", "_line_count"]

    def __init__(self, storage: MultiStorage, input_id: int, slope_k, bead_width, initial_indent=None, line_count=None, delete_old=False):
        super().__init__(storage, [input_id], algo=get_cut_lines, delete_old=delete_old)
        self._specification = raster_spec
        self._slope_k = slope_k
        self._bead_width = bead_width
        self._initial_indent = initial_indent
        self._line_count = line_count

    def _call_algo(self, input_geom_list=None):
        return self._algo(input_geom_list[0], self._slope_k, self._bead_width, self._initial_indent, self._line_count)

    def _validate(self):
        self._specification.deep_validation(
            {"poly_id": self._storage.get_primitive_list_by_id(self._input_geom_list[0])})


class Cut(ApplyAlgCommand):
    __slots__ = ["coord_for_cut", "cut_area", "at_existed_points"]

    def __init__(self, storage: MultiStorage, input_geom_id, delete_old, coord_for_cut, cut_area, at_existed_points):
        super().__init__(storage, [input_geom_id], algo=cut, delete_old=delete_old)
        self._specification = cut_spec
        self.coord_for_cut = coord_for_cut
        self.cut_area = cut_area
        self.at_existed_points = at_existed_points

    def _call_algo(self, input_geom_list=None):
        self._validate()
        return self._algo(input_geom_list[0], self.coord_for_cut, self.cut_area, self.at_existed_points)

    def _validate(self):
        self._specification.deep_validation(
            {"geom_id": self._storage.get_primitive_list_by_id(self._input_geom_list[0])})


class CreateGroup(ApplyAlgCommand):

    def __init__(self, storage: MultiStorage, input_geom_id_list, delete_old=True):
        super().__init__(storage, input_geom_id_list, algo=create_new_group, delete_old=delete_old)
        self._specification = new_group_spec

    def _call_algo(self, input_geom_list=None):
        self._validate()
        return self._algo(input_geom_list)


class DisbandGroup(ApplyAlgCommand):

    def __init__(self, storage: MultiStorage, input_group_id, delete_old=True):
        super().__init__(storage, [input_group_id], algo=disband_group, delete_old=delete_old)
        self._specification = group_disband_spec

    def _call_algo(self, input_geom_list=None):
        self._validate()
        return self._algo(input_geom_list[0])

    def _validate(self):
        self._specification.deep_validation(
            {"group_id": self._storage.get_primitive_list_by_id(self._input_geom_list[0])})


class AddObjectsToGroup(ApplyAlgCommand):

    def __init__(self, storage: MultiStorage, input_group_id, new_obj_id_list, delete_old=True):
        new_obj_id_list.insert(input_group_id)
        super().__init__(storage, new_obj_id_list, algo=add_objects_to_list, delete_old=delete_old)
        self._specification = add_to_group_spec

    def _call_algo(self, input_geom_list=None):
        self._validate()
        return self._algo(input_geom_list[0], input_geom_list[1:])

    def _validate(self):
        self._specification.deep_validation(
            {"group_id": self._storage.get_primitive_list_by_id(self._input_geom_list[0]),
             "id_list": self._storage.get_primitive_list_by_id(self._input_geom_list[1:])})


class Equidistant(ApplyAlgCommand):
    __slots__ = ["_distance_list", "_simple_buffer", "_difference", "_additional_args"]

    def __init__(self, storage: MultiStorage, input_id, distance_list: list, simple_buffer, difference, delete_old=False, **kwargs):
        super().__init__(storage, [input_id], algo=serial_buffer, delete_old=delete_old)
        self._specification = equidistant_spec
        self._distance_list = distance_list
        self._simple_buffer = simple_buffer
        self._difference = difference
        self._additional_args = kwargs

    def _call_algo(self, input_geom_list=None):
        return self._algo(input_geom_list[0], self._distance_list, self._simple_buffer, self._difference, **self._additional_args)

    def _validate(self):
        self._specification.deep_validation(
            {"poly_id": self._storage.get_primitive_list_by_id(self._input_geom_list[0])})
