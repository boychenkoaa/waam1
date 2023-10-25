from copy import deepcopy

from backend.Repo import MultiStorage
from backend.Specifications import move_spec, rotate_spec, revers_spec, add_point_spec, add_point_to_poly_spec, \
    remove_point_spec, remove_point_from_poly_spec, move_point_spec, move_point_poly_spec, move_point_gg_spec
from backend.commands.RepoCommands import iCommand, Response
from base.geom.raw.raw import scale


class EditCommand(iCommand):
    __slots__ = ["_geom_id_list"]

    def __init__(self, storage: MultiStorage, input_geom_id_list):
        super().__init__(storage)
        self._geom_id_list = input_geom_id_list

    def do(self):
        pass

    def redo(self):
        self.do()

    def _validate(self):
        self._specification.deep_validation({"id_list": self._storage.get_primitive_list_by_id(self._geom_id_list)})


class Move(EditCommand):
    __slots__ = ["_vector", "__is_moved"]

    def __init__(self, storage: MultiStorage, input_geom_id_list: int, vec: tuple):
        super().__init__(storage, input_geom_id_list)
        self._specification = move_spec
        self._vector = vec
        self.__is_moved = False

    def do(self):
        self._validate()
        for id_ in self._geom_id_list:
            self._storage[id_].geom.move_all(self._vector)
        self.__is_moved = True
        return Response(id_list_redraw=self._geom_id_list)

    def undo(self):
        if self.__is_moved:
            for id_ in self._geom_id_list:
                self._storage[id_].geom.move_all(scale(self._vector, -1))
            self.__is_moved = False
            return Response(id_list_redraw=self._geom_id_list)
        else:
            return Response()


class Rotation(EditCommand):
    __slots__ = ["_rot_center", "_angle", "__is_rotate"]

    def __init__(self, storage: MultiStorage, input_geom_id_list, center: tuple, rot_angle: float):
        super().__init__(storage, input_geom_id_list)
        self._specification = rotate_spec
        self._rot_center = center
        self._angle = rot_angle
        self.__is_rotate = False

    def do(self):
        self._validate()
        for id_ in self._geom_id_list:
            self._storage[id_].geom.rotate(self._rot_center, self._angle)
        self.__is_rotate = True
        return Response(id_list_redraw=self._geom_id_list)

    def undo(self):
        if self.__is_rotate:
            for id_ in self._geom_id_list:
                self._storage[id_].geom.rotate(self._rot_center, -self._angle)
            self.__is_rotate = False
            return Response(id_list_redraw=self._geom_id_list)
        else:
            return Response()


class Revers(EditCommand):
    __slots__ = "__is_reversed"

    def __init__(self, storage: MultiStorage, input_geom_id_list):
        super().__init__(storage, input_geom_id_list)
        self._specification = revers_spec
        self.__is_reversed = False

    def do(self):
        self._validate()
        for id_ in self._geom_id_list:
            self._storage[id_].geom.revers()
        self.__is_reversed = True
        return Response(id_list_redraw=self._geom_id_list)

    def undo(self):
        if self.__is_reversed:
            for id_ in self._geom_id_list:
                self._storage[id_].geom.revers()
            self.__is_reversed = False
            return Response(id_list_redraw=self._geom_id_list)
        else:
            return Response()


class AddPointToEdgeCenter(EditCommand):
    __slots__ = ["__prev_point_ind", "_new_point_id", "_new_point_coord"]

    def __init__(self, storage: MultiStorage, input_geom_id: int, prev_point_ind: int):
        super().__init__(storage, [input_geom_id])
        self._specification = add_point_spec
        self.__prev_point_ind = prev_point_ind
        self._new_point_id = None
        self._new_point_coord = None

    def do(self):
        self._new_point_id = self._storage[self._geom_id_list[0]].geom.insert(self.__prev_point_ind + 1)
        self._new_point_coord = self._storage[self._geom_id_list[0]].geom.p(self._new_point_id)
        return Response(id_list_redraw=self._geom_id_list)

    def undo(self):
        if self._new_point_id is not None:
            # удаляем точку
            self._storage[self._geom_id_list[0]].geom.rem_id(self.__prev_point_ind + 1)
            return Response(id_list_redraw=self._geom_id_list)
        else:
            return Response()

    def _validate(self):
        self._specification.deep_validation({"geom_id": self._storage.get_primitive_list_by_id(self._geom_id_list)})


class AddPointToPolyEdgeCenter(EditCommand):  # надо ли - ?
    __slots__ = ["__prev_point_ind", "_new_point_id", "_new_point_coord"]

    def __init__(self, storage: MultiStorage, input_geom_id: tuple, prev_point_ind: tuple):
        super().__init__(storage, [input_geom_id])
        self._specification = add_point_to_poly_spec
        self.__prev_point_ind = prev_point_ind
        self._new_point_id = None
        self._new_point_coord = None

    def do(self):
        self._validate()
        new_index = (self.__prev_point_ind[0], self.__prev_point_ind[1] + 1)
        self._new_point_id = self._storage[self._geom_id_list[0]].geom.insert(new_index)
        self._new_point_coord = self._storage[self._geom_id_list[0]].geom.p(self._new_point_id)
        return Response(id_list_redraw=self._geom_id_list)

    def undo(self):
        if self._new_point_id is not None:
            # удаляем точку
            prev_index = (self.__prev_point_ind[0], self.__prev_point_ind[1] + 1)
            self._storage[self._geom_id_list[0]].geom.rem_id(prev_index)
            return Response(id_list_redraw=self._geom_id_list)
        else:
            return Response()

    def _validate(self):
        self._specification.deep_validation({"poly_id": self._storage.get_primitive_list_by_id(self._geom_id_list)})


class RemPoint(EditCommand):
    __slots__ = ["__point_ind", "_rem_point_id", "_point", "__deleted_geom"]

    def __init__(self, storage: MultiStorage, input_geom_id: int, point_ind):
        super().__init__(storage, [input_geom_id])
        self._specification = remove_point_spec
        self.__point_ind = point_ind
        self._rem_point_id = None
        self._point = None
        self.__deleted_geom = None

    def do(self):
        self._validate()
        self._point = self._storage[self._geom_id_list[0]].geom[self.__point_ind]
        self._rem_point_id = self._storage[self._geom_id_list[0]].geom.pop(self.__point_ind)
        if len(self._storage[self._geom_id_list[0]].geom) == 0:  # удаляем объект!
            self.__deleted_geom = deepcopy(self._storage[self._geom_id_list[0]].geom)
            self._storage.rem_obj(self._geom_id_list[0])
            return Response(id_list_delete=self._geom_id_list)

        return Response(id_list_redraw=self._geom_id_list)

    def undo(self):
        if self._rem_point_id is not None:
            if self.__deleted_geom is not None:
                self._geom_id_list = self._storage.add_geom(self.__deleted_geom)
                current_geom = self.__deleted_geom
            else:
                current_geom = self._storage[self._geom_id_list[0]].geom

            if self._point not in current_geom:
                current_geom[self._rem_point_id] = self._point

            current_geom.insert(self.__point_ind, self._point)

            if self.__deleted_geom is not None:
                return Response(id_list_add=[self._geom_id_list])
            else:
                return Response(id_list_redraw=[self._geom_id_list])
        else:
            return Response()

    def _validate(self):
        self._specification.deep_validation({"geom_id": self._storage.get_primitive_list_by_id(self._geom_id_list)})


class RemPointFromPoly(EditCommand):
    __slots__ = ["__point_ind", "_rem_point_id", "_point"]

    def __init__(self, storage: MultiStorage, input_geom_id: int, point_ind):
        super().__init__(storage, [input_geom_id])
        self._specification = remove_point_from_poly_spec
        self.__point_ind = point_ind
        self._rem_point_id = None
        self._point = None

    def do(self):
        self._validate()
        self._point = self._storage[self._geom_id_list[0]].geom[self.__point_ind]
        self._rem_point_id = self._storage[self._geom_id_list[0]].geom.pop(self.__point_ind)
        return Response(id_list_redraw=self._geom_id_list)

    def undo(self):
        if self._rem_point_id is not None:
            current_geom = self._storage[self._geom_id_list[0]].geom
            if self._point not in current_geom:
                current_geom[self._rem_point_id] = self._point
            current_geom.insert(self.__point_ind, self._point)
            return Response(id_list_redraw=self._geom_id_list)
        else:
            return Response()

    def _validate(self):
        self._specification.deep_validation({"poly_id": self._storage.get_primitive_list_by_id(self._geom_id_list)})


class MovePoint(EditCommand):
    __slots__ = ["__point_ind", "_point_id", "_new_point_coord", "_old_point_coord"]

    def __init__(self, storage: MultiStorage, input_geom_id: int, point_ind, new_coord: tuple):
        super().__init__(storage, [input_geom_id])
        self._specification = move_point_spec
        self.__point_ind = point_ind
        self._new_point_coord = new_coord
        self._point_id = None
        self._old_point_coord = None

    def do(self):
        self._validate()
        self._old_point_coord = self._storage[self._geom_id_list[0]].geom[self.__point_ind]
        self._point_id = self._storage[self._geom_id_list[0]].geom.i(self.__point_ind)
        self._storage[self._geom_id_list[0]].geom.move(self.__point_ind, self._new_point_coord)
        return Response(id_list_redraw=self._geom_id_list)

    def undo(self):
        if self._point_id is not None:
            self._storage[self._geom_id_list[0]].geom.move(self.__point_ind, self._old_point_coord)
            return Response(id_list_redraw=self._geom_id_list)
        else:
            return Response()

    def _validate(self):
        self._specification.deep_validation({"geom_id": self._storage.get_primitive_list_by_id(self._geom_id_list)})


class MovePointFromPoly(EditCommand):
    __slots__ = ["__point_ind", "_point_id", "_new_point_coord", "_old_point_coord"]

    def __init__(self, storage: MultiStorage, input_geom_id: int, point_ind, new_coord: tuple):
        super().__init__(storage, [input_geom_id])
        self._specification = move_point_poly_spec
        self.__point_ind = point_ind
        self._new_point_coord = new_coord
        self._point_id = None
        self._old_point_coord = None

    def do(self):
        self._validate()
        self._old_point_coord = self._storage[self._geom_id_list[0]].geom[self.__point_ind]
        self._point_id = self._storage[self._geom_id_list[0]].geom.find(self._old_point_coord)
        self._storage[self._geom_id_list[0]].geom.move(self.__point_ind, self._new_point_coord)
        return Response(id_list_redraw=self._geom_id_list)

    def undo(self):
        if self._point_id is not None:
            self._storage[self._geom_id_list[0]].geom.move(self.__point_ind, self._old_point_coord)
            return Response(id_list_redraw=self._geom_id_list)
        else:
            return Response()

    def _validate(self):
        self._specification.deep_validation({"poly_id": self._storage.get_primitive_list_by_id(self._geom_id_list)})


class MovePointGG(EditCommand):
    __slots__ = ["__point_id", "_new_point_coord", "_old_geom"]

    def __init__(self, storage: MultiStorage, input_geom_id: int, point_ind, new_coord: tuple):
        super().__init__(storage, [input_geom_id])
        self._specification = move_point_gg_spec
        self.__point_id = point_ind
        self._new_point_coord = new_coord
        self._old_geom = None

    def do(self):
        self._validate()
        self._old_geom = deepcopy(self._storage[self._geom_id_list[0]].geom)
        self._storage[self._geom_id_list[0]].geom.move_id(self.__point_id, self._new_point_coord)
        return Response(id_list_redraw=self._geom_id_list)

    def undo(self):
        if self._old_geom is not None:
            self._storage[self._geom_id_list[0]].geom = self._old_geom
            return Response(id_list_redraw=self._geom_id_list)
        else:
            return Response()

    def _validate(self):
        self._specification.deep_validation({"gg_id": self._storage.get_primitive_list_by_id(self._geom_id_list)})

