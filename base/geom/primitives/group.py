from copy import deepcopy


class Group:
    __slots__ = ["_primitives"]

    def __init__(self, primitives: list):
        self._primitives = primitives

    def get_primitive_list(self):
        return deepcopy(self._primitives)

    @property
    def type(self):
        return "Group"

    def move_all(self, vector: tuple):
        for prim in self._primitives:
            prim.move_all(vector)

    def rotate(self, rotation_center: tuple, angle: float):
        for prim in self._primitives:
            prim.rotate(rotation_center, angle)

    def segments(self):
        ans = []
        for prim in self._primitives:
            ans.extend(prim.segments())
        return ans

    def points(self):  # массив массивов точек - более логично
        all_points = []
        for prim in self._primitives:
            all_points.append(prim.points())
        return all_points

    @property
    def raw(self):  # проверить, как работает, особенно с полигонами
        prim_ids_list = []
        for prim in self._primitives:
            prim_ids_list.append(prim.raw)
        return prim_ids_list
