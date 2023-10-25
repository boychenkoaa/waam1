import string
import traceback
from copy import deepcopy
import pydantic
from backend.GeomObject import CoordinateSystem, WCS
from backend.slices import Slice
from base.exceptions import ValidationError
from base.geom.primitives.dcel import DCEL
from base.geom.primitives.geomgraph import GeomGraph
from base.geom.primitives.linear import PLine, Polygon, PointChain, Contour
from base.geom.primitives.group import Group
from typing import Any


class Parameter:
    __slots__ = ["_name", "_count", "_type", "_expected_values", "_description", "_default_value"]

    def __init__(self, name: str, count: int, param_type, description: str, default_value: Any):
        self._name = name
        self._count = count
        self._type = param_type
        self._description = description
        self._default_value = default_value

    @staticmethod
    def _int_tuple_check(input_val):
        return True if (type(input_val) == tuple) and all(type(x) == int for x in input_val) else False

    @staticmethod
    def _float_tuple_check(input_val):
        return True if (type(input_val) == tuple) and all(type(x) in [int, float] for x in input_val) else False

    def _type_check(self, val):
        if self.type == "IntTuple":
            return self._int_tuple_check(val)
        elif self.type == "FloatTuple":
            return self._float_tuple_check(val)
        else:
            return type(val) == self.type

    def validate(self, real_param: list):
        return True if ((self.count and (len(real_param) == self.count)) or (not self.count and len(real_param))) and \
                (all(self._type_check(x) for x in real_param)) else False

    @property
    def type(self):
        return self._type

    @property
    def default_value(self):
        return self._default_value

    @property
    def expected_values(self):
        return self._expected_values

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def set_description(self, new_description=""):
        self._description = new_description

    def __repr__(self):
        return f"\nПараметр \"{self._name}\": {self._description}. count={self._count}, types={self._type}, " \
               f"expected values={self._expected_values}"

    @property
    def count(self):
        return self._count


class IDParameter(Parameter):

    __slots__ = "_inner_type_list"

    def __init__(self, name: str, count: int, param_type, descript: str, default_value: Any, inner_type_list=None):
        super().__init__(name, count, param_type, descript, default_value)
        self._inner_type_list = inner_type_list

    def deep_validate(self, real_param: list):
        return True if ((self.count and (len(real_param) == self.count)) or (not self.count and len(real_param))) and \
                (all(type(x) in self.inner_type for x in real_param)) else False

    def set_inner_type_list(self, type_list: list):
        self._inner_type_list = type_list
        return self

    @property
    def inner_type(self):
        return self._inner_type_list


class Specification:
    __slots__ = ["_spec_list"]

    def __init__(self, specification_list: list):
        self._spec_list = specification_list

    def get_id_parameters(self):
        return filter(lambda x: isinstance(x, IDParameter), self._spec_list)

    def validate(self, values_dict: dict) -> bool:  # проверка как списка произвольной/ единичной длинны
        for param in self._spec_list:
            value = values_dict.get(param.name)
            if value is None and param.default_value is not None:
                continue
            if not isinstance(value, list):
                value = [value]
            if not param.validate(value):
                # raise ValidationError(f"Wrong type: {type(value), param.type}")
                return False
        return True

    def deep_validation(self, values_dict: dict):
        for param in self.get_id_parameters():
            if param.inner_type is not None:
                value = values_dict.get(param.name)
                if not isinstance(value, list):
                    value = [value]
                if not param.deep_validate(value):
                    raise ValidationError(f"Wrong type: {type(value), param.type}")
        return True

    def __repr__(self):
        return f"Specification list={[param for param in self._spec_list]}"


geom_id = Parameter("geom_id", 1, int, "ID_геометрического объекта", None)
polygon_id = IDParameter("poly_id", 1, int, "Полигон", None, [Polygon])
contour_id = IDParameter("contour_id", 1, int, "Контур", None, [Contour])
pline_id = IDParameter("pline_id", 1, int, "Полилиния", None, [PLine])
gg_id = IDParameter("gg_id", 1, int, "Геометрический граф", None, [GeomGraph])
dcel_id = IDParameter("dcel_id", 1, int, "РСДС", None, [DCEL])
group_id = IDParameter("group_id", 1, int, "Группа", None, [Group])
editable_types_id = IDParameter("geom_id", 1, int, "Редактируемый геометрический объект", None, [PLine, Contour])  # переименовать
linear_type_id = IDParameter("geom_id", 1, int, "Линейный геометрический объект", None, [PLine, Contour, Polygon])
nonlinear_type_id = IDParameter("geom_id", 1, int, "Нелинейный геометрический объект", None, [DCEL, GeomGraph])
display_types_id = IDParameter("geom_id", 1, int, "Отображаемый геометрический объект", None, [PLine, Contour, Polygon, Group])
base_type_id = IDParameter("geom_id", 1, int, "Базовый геометрический объект", None, [PLine, Contour, Polygon, DCEL, GeomGraph])
all_type_id = IDParameter("geom_id", 1, int, "Геометрический объект", None, [PLine, Contour, Polygon, DCEL, GeomGraph, Group])

id_list = Parameter("id_list", 0, int, "список ID", None)
all_display_types_id_list = IDParameter("id_list", 0, int, "Список отображаемых геометрических объектов", None, [PLine, Contour, Polygon, Group])
linear_type_id_list = IDParameter("id_list", 0, int, "Список линейных геометрических объектов", None, [PLine, Contour, Polygon])
contour_id_list = IDParameter("id_list", 0, int, "Список контуров", None, [Contour])
polygon_id_list = IDParameter("id_list", 0, int, "Список полигонов", None, [Polygon])

slice_id = IDParameter("slice_id", 1, int, "ID слайса", -1, [Slice])
new_slice_id = IDParameter("new_slice_id", 1, int, "ID слайса", -1, [Slice])

pline = Parameter("pline", 1, PLine, "Полилиния", None)
contour = Parameter("contour", 1, Contour, "Замкнутый контур", None)
holes = Parameter("holes", 0, Contour, "Список контуров", [])  # нужно ли так делать?
polygon = Parameter("polygon", 1, Polygon, "Полигон из замкнутого внешнего контура и замкнутых дырок", None)
group = Parameter("group", 1, Group, "Группа", None)
geom_graph = Parameter("geom_graph", 1, GeomGraph, "Геометрический граф", None)

point = Parameter("point", 1, "FloatTuple", "Точка", None)
point_list = Parameter("point_list", 0, "FloatTuple", "Список точек", [])
list_of_point_list = Parameter("list_of_point_list", 0, "point_list", "Список списков точек", [])
segment = Parameter("segment", 2, "FloatTuple", "Отрезок", None)
segment_list = Parameter("segment_list", 0, segment, "Список отрезков", [])
geom_obj = Parameter("geom_obj", 1, "geom", "Геометрический объект", None)
geom_list = Parameter("geom_list", 0, "geom", "Список нужных геометрических объектов", [])
vector = Parameter("vector", 2, tuple, "Направленный отрезок из двух точек", None)
rotation_center = Parameter("rotation_center", 1, tuple, "Точка центра поворота объекта", (0, 0))
rotation_angle = Parameter("rotation_angle", 1, float, "Угол поворота объекта", 0.)
point_ind = Parameter("point_ind", 1, int, "Точка", None)
prev_ind = Parameter("prev_ind", 1, int, "Точка начала ребра", None)
post_ind = Parameter("post_ind", 1, int, "Точка конца ребра", None)
poly_point_ind = Parameter("polygon_point_ind", 1, "IntTuple", "Точка полигона", None)
poly_prev_ind = Parameter("polygon_prev_ind", 1, "IntTuple", "Точка начала ребра полигона", None)
new_coord = Parameter("new_coord", 1, "FloatTuple", "Новые координаты объекта", None)
user_coord = Parameter("user_coord", 1, "FloatTuple", "Пользовательские координаты", None)
distance_list = Parameter("distance_list", 0, float, "Список дистанций смещения", [])
cut_holes = Parameter("cut_holes", 1, bool, "Параметр учёта отверстий", False)
without_shrink = Parameter("without_shrink", 1, bool, "Параметр сжатия", True)
slope = Parameter("slope", 1, float, "Угол наклона", 0.)
bead_width = Parameter("bead_width", 1, float, "Ширина валика", 3.)
initial_indent = Parameter("initial_indent", 1, float, "Стартовый отступ", 1.5)
line_count = Parameter("line_count", 1, int, "Количество линий", None)
displacement_vector = Parameter("displacement_vector", 1, "FloatTuple", "Вектор смещения", None)
area = Parameter("area", 1, float, "Максимальное расстояние до ближайшей точки", 1.)
only_from_existing = Parameter("only_from_existing", 1, bool, "Параметр учёта только существующих точек", True)
coord_system = Parameter("coordinate_system", 1, CoordinateSystem, "Система координат", WCS)
description = Parameter("description", 1, string, "Описание", "")


add_pline_spec = Specification([point_list])  # тут список точек, не примитив
add_poly_spec = Specification([point_list, list_of_point_list])
add_slice_spec = Specification([segment_list])
add_empty_slice_spec = Specification([coord_system, description])

remove_spec = Specification([all_display_types_id_list])

remove_slice_spec = Specification([slice_id])

change_active_slice_spec = Specification([slice_id, new_slice_id])

change_slice_description_spec = Specification([slice_id, description])

move_spec = Specification([all_display_types_id_list, displacement_vector])

replace_to_another_slice_spec = Specification([slice_id, new_slice_id, all_display_types_id_list])

copy_spec = Specification([all_display_types_id_list, displacement_vector])

rotate_spec = Specification([all_display_types_id_list, rotation_center, rotation_angle])

pline_cut_poly_spec = Specification([pline_id, polygon_id])

# проверить для полигона
cut_spec = Specification([editable_types_id, user_coord, area, only_from_existing])

add_point_spec = Specification([editable_types_id, prev_ind])

add_point_to_poly_spec = Specification([polygon_id, poly_prev_ind])

add_point_to_nonlinear_spec = Specification([nonlinear_type_id, prev_ind, post_ind])

remove_point_spec = Specification([editable_types_id, point_ind])

remove_point_from_poly_spec = Specification([polygon_id, poly_point_ind])

remove_point_from_nonlinear_spec = Specification([nonlinear_type_id, point_ind])

move_point_spec = Specification([editable_types_id, point_ind, new_coord])

move_point_poly_spec = Specification([polygon_id, point_ind, new_coord])

move_point_gg_spec = Specification([gg_id, point_ind, new_coord])

move_point_dcel_spec = Specification([dcel_id, point_ind, new_coord])

remove_collinear_spec = Specification([base_type_id])

equidistant_spec = Specification([polygon_id, distance_list, cut_holes, without_shrink])

revers_spec = Specification([linear_type_id_list])

convert_contours_to_poly_spec = Specification([contour_id_list])

convert_poly_to_contours_spec = Specification([polygon_id])

raster_spec = Specification([polygon_id, slope, bead_width, initial_indent, line_count])

sceleton_spec = Specification([polygon_id_list])

new_group_spec = Specification([all_display_types_id_list])
group_disband_spec = Specification([group_id])
add_to_group_spec = Specification([group_id, all_display_types_id_list])


get_type_spec = Specification([all_type_id])  # all_display_types_id_list - ?
get_data_spec = Specification([all_type_id])  # all_display_types_id_list - ?
get_dp_spec = Specification([all_type_id])  # all_display_types_id_list - ?
get_copy_spec = Specification([all_display_types_id_list, displacement_vector])
get_move_spec = Specification([all_display_types_id_list, displacement_vector])
get_rotation_spec = Specification([all_display_types_id_list, rotation_center, rotation_angle])
get_slice_data_spec = Specification([slice_id])
get_add_slice_spec = Specification([segment_list])
get_equidistant_spec = Specification([polygon_id, distance_list, cut_holes, without_shrink])
get_raster_spec = Specification([polygon_id, slope, bead_width, initial_indent, line_count])

if __name__ == "__main__":
    print(get_rotation_spec.validate({"geom list": [1, 2, 3], "rotation center": (5.4, 5.3), "rotation angle": 55.4}))
    print(get_rotation_spec.validate({"geom list": [1, 2, 3], "rotation center": (5.4, 5.3), "rotation angle": 55.4}))
    print(get_rotation_spec.validate({"geom list": [1, 2, 3], "rotation center": (5.4, 5.3), "rotation angle": 55.4}))
    print(
        get_rotation_spec.validate({"id list": [1, 2, 3.5, 4, 5, 6, 7], "rotation center": (5.4, 5.3), "rotation angle": 55.4}))
    print(
        get_rotation_spec.validate({"id list": [1, 2, 3, 4, 5, 6, 7], "rotation center": (5.4, 5.3, 4), "rotation angle": 55.4}))
    print(get_rotation_spec.validate({"id list": [1], "rotation center": (5.4, 5.3), "rotation angle": 55.4}))
    print(get_rotation_spec.validate({"id list": [1], "rotation center": (5.4, 5.3), "rotation angle": (55.4, 8.342)}))
