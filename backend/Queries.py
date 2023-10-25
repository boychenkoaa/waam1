from copy import copy, deepcopy

from backend.GeomObject import DPlineP, WCS
from backend.Repo import GeomObjStorage, MultiStorage
from backend.Specifications import get_type_spec, get_add_slice_spec, get_raster_spec, get_move_spec, get_rotation_spec, \
    get_copy_spec, get_equidistant_spec, get_dp_spec, get_slice_data_spec, get_data_spec
from base.geom.algo.algo import copy_geoms, get_cut_lines, add_slice
from base.geom.algo.algo import buffer
from base.geom.algo.buffer import serial_buffer


# возможно перенести куда-то в другое место
class GuiObg:
    def __init__(self, id_: int, geom_type, data, disp_prop: dict):
        self._id = id_
        self._type = geom_type  # polygon, polyline, contour
        self._raw_data = data  # [(0,0), (10,10)] - for polyline/contour
                              # [[exteriour], [hole_1], [hole_2] - for polygon
        self._properties = disp_prop  # dict {color:"red", width: 0.1}

    def change_properties(self, update_dict):
        self._properties.update(update_dict)

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def raw_data(self):
        return self._raw_data

    @property
    def properties(self):
        return self._properties


class iSpec:  # под снос - ?
    def is_valid(self, id_):
        pass

    def __and__(self, other):
        pass

    def __or__(self, other):
        pass


class iQuery:
    __slots__ = ["_storage", "_query_result", "_specification"]

    def __init__(self, storage):
        self._storage = storage
        self._query_result = None
        self._specification = None

    def do(self):
        pass

    def _validate(self):
        pass


class qGetType(iQuery):
    __slots__ = "_id"

    def __init__(self, storage, id_):
        super().__init__(storage)
        self._specification = get_type_spec
        self._id = id_

    def do(self):
        self._validate()
        self._query_result = self._storage[self._id].geom_type
        return self._query_result

    def _validate(self):
        self._specification.deep_validation({"geom_id": self._storage[self._id]})


class qGetData(iQuery):
    __slots__ = "_id"

    def __init__(self, storage, id_):
        super().__init__(storage)
        self._specification = get_data_spec
        self._id = id_

    def do(self):
        self._validate()
        self._query_result = self._storage[self._id].geom.points()
        return self._query_result

    def _validate(self):
        self._specification.deep_validation({"geom_id": self._storage[self._id]})


class qGetSliceData(iQuery):
    __slots__ = "_id"

    def __init__(self, storage, id_):
        super().__init__(storage)
        self._specification = get_slice_data_spec
        self._id = id_

    def do(self):
        self._validate()
        # вернуть все примитивы на слайсе
        self._query_result = []
        all_geom_ids = self._storage.get_all_geoms_at_slice(self._id)
        for id_ in all_geom_ids:
            new_gui_obg = GuiObg(id_, self._storage[id_].geom_type, self._storage[id_].geom.points(), self._storage[id_].DP)
            self._query_result.append(new_gui_obg)
        return self._query_result

    def _validate(self):
        self._specification.deep_validation({"geom_id": self._storage[self._id]})


class qGetAll(iQuery):
    def __init__(self, storage):
        super().__init__(storage)

    def do(self):
        self._query_result = []
        geom_id_list = self._storage.get_id_list()
        for geom_id in geom_id_list:
            new_gui_obg = GuiObg(geom_id, self._storage[geom_id].geom_type, self._storage[geom_id].geom.points(), self._storage[geom_id].DP)
            self._query_result.append(new_gui_obg)
        return self._query_result


class qGetAllSlices(iQuery):
    def __init__(self, storage):
        super().__init__(storage)

    def do(self):
        return self._storage.get_all_slices()


class qGetAllGroups(iQuery):
    def __init__(self, storage):
        super().__init__(storage)

    def do(self):
        return self._storage.get_all_groups()


class qGetIDlist(iQuery):
    def __init__(self, storage):
        super().__init__(storage)

    def do(self):
        self._query_result = self._storage.get_id_list()
        return self._query_result


class qGetDP(iQuery):
    __slots__ = "_id"

    def __init__(self, storage, id_):
        super().__init__(storage)
        self._specification = get_dp_spec
        self._id = id_

    def do(self):
        self._validate()
        self._query_result = self._storage[self._id].DP
        return self._query_result

    def _validate(self):
        self._specification.deep_validation({"geom_id": self._storage[self._id]})


class qAlgo(iQuery):  # добавить валидацию
    __slots__ = ["_input_ids", "_algo"]

    def __init__(self, storage: MultiStorage, input_id_list: list, algo):
        super().__init__(storage)
        self._input_ids = copy(input_id_list)
        self._algo = algo

    def _call_algo(self, input_geom_list):
        return []

    def do(self):
        self._validate()
        input_geom_list = [self._storage[input_id].geom for input_id in self._input_ids]
        output_geom_list = deepcopy(self._call_algo(input_geom_list))
        return output_geom_list

    def _validate(self):
        self._specification.deep_validation({"id_list": self._storage.get_primitive_list_by_id(self._input_ids)})


class qAddSlice(qAlgo):  # автоматически генерируется новый объект слайса
    __slots__ = ["_segment_list", "_cs"]

    def __init__(self, storage: MultiStorage, segment_list, new_CS=WCS):
        super().__init__(storage, input_id_list=[], algo=add_slice)
        self._specification = get_add_slice_spec
        self._segment_list = segment_list
        self._cs = new_CS

    def _call_algo(self, input_geom_list):
        return self._algo(self._segment_list)  # добавляем сечение на слайс


class qAddBuffer(qAlgo):
    # __slots__ = "_distance"
    __slots__ = ["_distance_list", "_simple_buffer", "_difference", "_additional_args"]

    def __init__(self, storage: MultiStorage, input_id: list, distance_list: list, simple_buffer=True, difference=False, **kwargs):
        super().__init__(storage, [input_id], algo=serial_buffer)
        self._specification = get_equidistant_spec
        self._distance_list = distance_list
        self._simple_buffer = simple_buffer
        self._difference = difference
        self._additional_args = kwargs

    def _call_algo(self, input_geom_list=None):
        return self._algo(input_geom_list[0], self._distance_list, self._simple_buffer, self._difference)

    def do(self):
        geom_list = super().do()
        gui_obg_list = []
        for geom in geom_list:
            # линии или контура - ?
            gui_obg_list.append(GuiObg(-1, "PLine", geom.points(), DPlineP))
        return gui_obg_list


class qCopy(qAlgo):  # Move - то же самое
    __slots__ = "_vector"

    def __init__(self, storage: MultiStorage, input_geom_id_list, vec: tuple):
        super().__init__(storage, input_id_list=input_geom_id_list, algo=copy_geoms)
        self._specification = get_copy_spec
        self._vector = vec

    def _call_algo(self, input_geom_list):
        return self._algo(input_geom_list, copy(self._vector))


class qRotation(qAlgo):
    __slots__ = ["_rot_center", "_angle"]

    def __init__(self, storage: MultiStorage, input_geom_id_list, center: tuple, rot_angle: float):
        super().__init__(storage, input_id_list=input_geom_id_list, algo=None)
        self._specification = get_rotation_spec
        self._rot_center = center
        self._angle = rot_angle

    def _call_algo(self, input_geom_list):
        ans = []
        for geom_obg in input_geom_list:
            ans.append(deepcopy(geom_obg.geom).rotate(self._rot_center, self._angle))
        return ans


class qMove(qAlgo):
    __slots__ = ["_vector"]

    def __init__(self, storage: MultiStorage, input_geom_id_list, vector: tuple):
        super().__init__(storage, input_id_list=input_geom_id_list, algo=None)
        self._specification = get_move_spec
        self._vector = vector

    def _call_algo(self, input_geom_list):
        ans = []
        for geom_obg in input_geom_list:
            ans.append(deepcopy(geom_obg.geom).move_all(self._vector))
        return ans


class qRaster(qAlgo):
    __slots__ = ["_slope_k", "_bead_width", "_initial_indent", "_line_count"]

    def __init__(self, storage: MultiStorage, input_id: int, slope_k, bead_width, initial_indent=None, line_count=None):
        super().__init__(storage, [input_id], algo=get_cut_lines)
        self._specification = get_raster_spec
        self._slope_k = slope_k
        self._bead_width = bead_width
        self._initial_indent = initial_indent
        self._line_count = line_count

    def _call_algo(self, input_geom_list):
        return self._algo(input_geom_list[0], self._slope_k, self._bead_width, self._initial_indent, self._line_count)

    def do(self):
        geom_list = super().do()
        gui_obg_list = []
        for geom in geom_list:
            # линии или контура - ?
            gui_obg_list.append(GuiObg(-1, "PLine", geom.points(), DPlineP))
        return gui_obg_list




