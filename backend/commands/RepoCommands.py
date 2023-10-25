from backend.GeomObject import WCS
from backend.Specifications import remove_slice_spec, remove_spec, change_active_slice_spec, \
    replace_to_another_slice_spec, change_slice_description_spec
from base.geom.algo.algo import add_slice
from base.geom.primitives.linear import Polygon, Contour, PLine
from backend.Queries import iQuery
from backend.Repo import GeomObject, MultiStorage
from copy import deepcopy


class Response:
    __slots__ = ["_id_list_redraw", "_id_list_delete", "_id_list_add"]

    def __init__(self, id_list_redraw=None, id_list_delete=None, id_list_add=None):
        self._id_list_redraw = id_list_redraw if id_list_redraw is not None else []
        self._id_list_delete = id_list_delete if id_list_delete is not None else []
        self._id_list_add = id_list_add if id_list_add is not None else []

    def unpack(self):
        return self._id_list_redraw, self._id_list_delete, self._id_list_add


class iCommand:
    __slots__ = ["_storage", "_specification"]

    def __init__(self, storage):
        self._storage = storage
        self._specification = None

    def _validate(self):
        pass

    def do(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass


class BaseAdd(iCommand):
    __slots__ = ["__primitive", "_raw", "__coordinate_system", "_id", "__geom", "__is_complete"]

    def __init__(self, storage: MultiStorage, raw_content):
        super().__init__(storage)
        self._specification = None
        self._raw = raw_content
        self.__primitive = None
        self._id = None
        self.__is_complete = None

    def do(self):
        pass

    def undo(self):
        if self.__is_complete:
            self._storage.rem_obj(self._id)
            self.__is_complete = False
            return Response(id_list_delete=[self._id])
        else:
            return Response()

    def redo(self):
        self._storage.add_from_archive(self._id)
        self.__is_complete = True
        return Response(id_list_add=[self._id])

    def __del__(self):
        if not self.__is_complete and self._id is not None:
            self._storage.delete(self._id)


class Add(BaseAdd):

    def __init__(self, storage: MultiStorage, raw_content):
        super().__init__(storage, raw_content)

    def do(self):
        if self._raw[0] == self._raw[len(self._raw)-1]:
            self.__primitive = Contour(self._raw[:-1])
        else:
            self.__primitive = PLine(self._raw)
        self._id = self._storage.add_geomobject(GeomObject(self.__primitive))
        self.__is_complete = True
        return Response(id_list_add=[self._id])


class AddPolygon(BaseAdd):

    def __init__(self, storage: MultiStorage, raw_contour, raw_holes):
        super().__init__(storage, [raw_contour, raw_holes])

    def do(self):
        self.__primitive = Polygon(self._raw[0], self._raw[1])
        self._id = self._storage.add_geomobject(GeomObject(self.__primitive))
        self.__is_complete = True
        return Response(id_list_add=[self._id])


class Remove(iCommand):
    __slots__ = ["_id_list", "__is_complete"]

    def __init__(self, storage: MultiStorage, geom_obj_id_list):
        super().__init__(storage)
        self._specification = remove_spec
        self._id_list = geom_obj_id_list
        self.__is_complete = False

    def do(self):
        self._validate()
        for id_ in self._id_list:
            self._storage.rem_obj(id_)
        self.__is_complete = True
        return Response(id_list_delete=self._id_list)

    def undo(self):
        if self.__is_complete:
            for id_ in self._id_list:
                self._storage.add_from_archive(id_)
            self.__is_complete = False
            return Response(id_list_add=self._id_list)
        else:
            return Response()

    def redo(self):
        if not self.__is_complete:
            self.__is_complete = True
            return self.do()

    def __del__(self):
        if self.__is_complete:
            for id_ in self._id_list:
                self._storage.delete(id_)

    def _validate(self):
        self._specification.deep_validation({"id_list": self._storage.get_primitive_list_by_id(self._id_list)})


# предложение Игорю каждый раз читать активный слайс
class AddEmptySlice(iCommand):
    __slots__ = ["_cs", "_slice_id", "_slice_obj",  "_description", "__is_complete"]

    def __init__(self, storage: MultiStorage, new_CS=WCS, description=""):
        super().__init__(storage)
        self._cs = new_CS
        self._slice_id = None
        self._description = description
        self.__is_complete = False
        self._slice_obj = None

    def do(self):
        self._validate()
        self._slice_id = self._storage.add_slice(self._cs, self._description)
        self.__is_complete = True
        return True

    def undo(self):
        if self.__is_complete:
            self._slice_obj = self._storage.pop_slice(self._slice_id)  # тут пустой слой
            self.__is_complete = False
            return True
        else:
            return False

    def redo(self):
        self._storage.restore_slice(self._slice_id, self._slice_obj, [])
        self.__is_complete = True
        return True


class AddSlice(iCommand):  # автоматически генерируется новый объект слайса, после все фронт перезагружается
    __slots__ = ["_segment_list", "_cs", "_slice_id", "_slice_obj", "__output_ids", "__is_complete"]

    def __init__(self, storage: MultiStorage, segment_list, new_CS=WCS):
        super().__init__(storage)
        self._cs = new_CS
        self._slice_id = None
        self._slice_obj = None
        self.__is_complete = False
        self.__output_ids = []

    def do(self):
        self._slice_id = self._storage.add_slice(self._cs)
        self.__output_ids = [self._storage.add_geomobject(GeomObject(geom)) for geom in deepcopy(add_slice(self._segment_list))]
        self.__is_complete = True
        return True

    def undo(self):
        if self.__is_complete:
            self._slice_obj = self._storage.pop_slice(self._slice_id)  # тут пустой слой
            for id_ in self.__output_ids:
                self._storage.rem_obj(id_)
            self.__is_complete = False
            return True
        else:
            return False

    def redo(self):
        self._storage.restore_slice(self._slice_id, self._slice_obj, [])
        for id_ in self.__output_ids:
            self._storage.add_from_archive(id_)
        self.__is_complete = True
        return True


class RemoveSlice(iCommand):
    __slots__ = ["_slice_id", "_slice_obj", "__is_complete", "_slice_content"]

    def __init__(self, storage: MultiStorage, slice_id):
        super().__init__(storage)
        self._specification = remove_slice_spec
        self._slice_id = slice_id
        self.__is_complete = False
        self._slice_obj = None
        self._slice_content = None

    def do(self):
        self._validate()
        self._slice_content = self._storage.get_all_geoms_at_slice(self._slice_id)
        self._slice_obj = self._storage.rem_slice(self._slice_id)
        # удалить весь контент на слайсе!!!
        for id_ in self._slice_content:
            self._storage.rem_obj(id_)
        self.__is_complete = True
        return True

    def undo(self):
        if self.__is_complete:
            self._storage.restore_slice(self._slice_id, self._slice_obj, self._slice_content)
            self.__is_complete = False
            return True
        else:
            return False

    def redo(self):
        self._storage.rem_slice(self._slice_id)
        for id_ in self._slice_content:
            self._storage.rem_obj(id_)
        self.__is_complete = True
        return True

    def _validate(self):
        self._specification.deep_validation({"slice_id": self._storage.get_slice(self._slice_id)})


class ChangeActiveSlice(iCommand):
    __slots__ = ["_new_active_slice_id", "_old_active_slice_id", "__is_complete"]

    def __init__(self, storage: MultiStorage, new_active_slice_id):
        super().__init__(storage)
        self._specification = change_active_slice_spec
        self._new_active_slice_id = new_active_slice_id
        self._old_active_slice_id = None
        self.__is_complete = False

    def do(self):
        self._validate()
        self._old_active_slice_id = self._storage.active_slice
        self._storage.change_active_slice(self._new_active_slice_id)
        self.__is_complete = True
        return True

    def undo(self):
        if self.__is_complete:
            self._storage.change_active_slice(self._old_active_slice_id)
            self.__is_complete = False
            return True
        else:
            return False

    def redo(self):
        self._storage.change_active_slice(self._new_active_slice_id)
        self.__is_complete = True
        return True

    def __del__(self):
        pass

    def _validate(self):
        self._specification.deep_validation({"slice_id": self._storage.get_slice(self._old_active_slice_id),
                                             "new_slice_id":  self._storage.get_slice(self._new_active_slice_id)})


class ReplaceToAnotherSlice(iCommand):
    __slots__ = ["_new_slice_id", "_old_slice_id", "_obj_id_list", "__is_complete"]

    def __init__(self, storage: MultiStorage, new_slice_id, old_slice_id, obj_id_list):
        super().__init__(storage)
        self._validate()
        self._specification = replace_to_another_slice_spec
        self._new_slice_id = new_slice_id
        self._old_slice_id = old_slice_id
        self._obj_id_list = obj_id_list
        self.__is_complete = False

    def do(self):
        self._storage.move_geoms_to_another_slice(self._new_slice_id, self._obj_id_list)
        self.__is_complete = True
        return True

    def undo(self):
        if self.__is_complete:
            self._storage.move_geoms_to_another_slice(self._old_slice_id, self._obj_id_list)
            self.__is_complete = False
            return True
        else:
            return False

    def redo(self):
        self._storage.move_geoms_to_another_slice(self._new_slice_id, self._obj_id_list)
        self.__is_complete = True
        return True

    def __del__(self):
        pass

    def _validate(self):
        self._specification.deep_validation({"slice_id": self._storage.get_slice(self._old_slice_id),
                                             "new_slice_id": self._storage.get_slice(self._new_slice_id),
                                             "id_list": self._storage.get_primitive_list_by_id(self._obj_id_list)})


class ChangeSliceDescription(iCommand):
    __slots__ = ["_slice_id", "_new_slice_descript", "_old_slice_descript", "__is_complete"]

    def __init__(self, storage: MultiStorage, slice_id, new_slice_description):
        super().__init__(storage)
        self._specification = change_slice_description_spec
        self._slice_id = slice_id
        self._new_slice_descript = new_slice_description
        self._old_slice_descript = None
        self.__is_complete = False

    def do(self):
        self._validate()
        self._old_slice_descript = self._storage.get_slice_description(self._slice_id)
        self._storage.change_slice_description(self._slice_id, self._new_slice_descript)
        self.__is_complete = True
        return True

    def undo(self):
        if self.__is_complete:
            self._storage.change_slice_description(self._slice_id, self._old_slice_descript)
            self.__is_complete = False
            return True
        else:
            return False

    def redo(self):
        self._storage.change_slice_description(self._slice_id, self._new_slice_descript)
        self.__is_complete = True
        return True

    def __del__(self):
        pass

    def _validate(self):
        self._specification.deep_validation({"slice_id": self._storage.get_slice(self._slice_id)})








