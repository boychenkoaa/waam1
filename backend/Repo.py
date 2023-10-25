from copy import deepcopy, copy

from backend.Groups import GroupContainer
# from email.headerregistry import Group

from backend.layers import Layers
from backend.slices import Slices, Slice
from base.geom.primitives.group import Group
from points.IDContainer import IDContainer, IDEntity
from points.idgenerator import SimpleIDGenerator
from backend.GeomObject import GeomIDEntity, GeomObject, WCS  # GeomContainer,
from points.Mediator import BaseMediatorClient, StorageMediator


# Монолитный тип геометрического репозитория
# внутреннее устройство: коллекция + группы
# коллекция -- словарь с id - ключами
# группы -- словарь. Ключи-имена групп. Значения - списки (упорядоченные).
# добавить страховки

class iStorage():
    def __init__(self):
        pass

    def __getitem__(self, id_):
        pass

    def __contains__(self, id_):
        pass

    def find(self, id_):
        pass

    def add_geom_obj(self, geom_obj):
        pass

    def rem_obj(self, id_):
        pass


class Storage(iStorage):
    __slots__ = ["_collection", "_id_generator"]

    def __init__(self):
        super().__init__()
        self._id_generator = SimpleIDGenerator()
        self._collection = IDContainer()  # !!

    def __getitem__(self, id_):
        assert (id_ in self)
        return self._collection[id_].value

    def __contains__(self, id_):
        return id_ in self._collection

    def find(self, id_: int):
        return self._collection.find_by_id(id_)

    def _new_id(self):
        return self._id_generator.new_id()

    def add(self, pline):
        id_ = self._new_id()
        self._collection.add(GeomIDEntity(id_, pline))
        return id_

    def rem_obj(self, id_):
        self._collection.rem(id_)

    def get_all(self):  # проверить!!
        collector = self._collection
        return [id_.value for id_ in self._collection]

    def __setitem__(self, id_, pline):
        self._collection[id_] = pline

    def get_id_list(self):  # проверить!!
        return [id_.id for id_ in self._collection]


class GeomObjStorage(iStorage):
    __slots__ = ["_collection", "_archive_collection", "_id_generator"]

    def __init__(self):
        super().__init__()
        self._id_generator = SimpleIDGenerator()
        self._collection = IDContainer()
        self._archive_collection = IDContainer()

    def __getitem__(self, id_):
        assert (id_ in self)
        return self._collection[id_].value

    def __setitem__(self, id_, geomobject: GeomObject):
        # assert (id_ in self)
        self._collection.add(GeomIDEntity(id_, geomobject))

    def __contains__(self, id_):
        return id_ in self._collection

    def __iter__(self):
        # проверить !!
        return self._collection.__iter__()

    def find(self, id_: int):
        return self._collection.find_by_id(id_)

    def _new_id(self):
        return self._id_generator.new_id()

    def add_geomobject(self, geomobject: GeomObject):
        id_ = self._new_id()
        self._collection.add(GeomIDEntity(id_, geomobject))
        return id_

    def add_from_archive(self, id_):
        assert (id_ in self._archive_collection)
        id_ent = deepcopy(self._archive_collection[id_])
        self._collection.add(id_ent)
        self._archive_collection.rem(id_)

    def rem_obj(self, id_):
        assert (id_ in self)
        id_ent = deepcopy(self._collection[id_])
        self._archive_collection.add(id_ent)
        self._collection.rem(id_)

    def delete(self, id_):
        assert (id_ in self._archive_collection)
        self._archive_collection.rem(id_)

    def get_id_list(self):
        return [geom_obj.id for geom_obj in self._collection]

    def get_primitive_list_by_id(self, id_list):
        return [self._collection[id_] for id_ in id_list]

    def clear(self):
        self._id_generator = SimpleIDGenerator()
        self._collection = IDContainer()
        self._archive_collection = IDContainer()


class MultiStorage(GeomObjStorage):
    __slots__ = ["_slices", "_groups"]

    def __init__(self):
        super().__init__()
        # автоматически создаётся слайс -1 и слой default
        self._slices = Slices()
        # self._layers = Layers()

    def add_slice(self, new_CS=WCS, new_description=""):  # нужно ли автоматически делать активным?
        new_id = self._slices.add_slice(new_CS, new_description)
        self._slices.set_active(new_id)
        return new_id

    def get_slice(self, slice_id):
        return self._slices.get_slice(slice_id)


    """
    def add_layer(self, name=None, is_visible=True, is_frozen=False, dp=None):  # нужно ли автоматически делать активным?
        new_id = self._layers.add_layer(name, is_visible, is_frozen, dp)
        self._layers.set_active(new_id)
        return new_id
            """

    def add_geomobject(self, geomobject: GeomObject):  # , layer_name=None
        id_ = super().add_geomobject(geomobject)
        self._slices.append([id_])
        # self._layers.append([id_], layer_name)
        return id_

    def add_from_archive(self, id_):
        super().add_from_archive(id_)
        self._slices.append(id_)

    def rem_obj(self, id_):
        super().rem_obj(id_)
        self._slices.delete_object(id_)

    def delete(self, id_):
        super().delete(id_)

    def restore_slice(self, id_, sl: Slice, geom_obj_list):
        active_sl = copy(self._slices.active)
        self._slices.add_by_id(id_, sl)
        self._slices.set_active(id_)  # нужно ли делать активным?
        self._slices.append(geom_obj_list)
        self._slices.set_active(active_sl)

    def rem_slice(self, s_id):  # -1 - автоматически активный, если удалили активный
        return self._slices.pop_slice(s_id)

    """
    def rem_layer(self, layer_name):  # "default" - автоматически активный, если удалили активный
        self._layers.remove_layer(layer_name)
    """

    def clear(self):
        super().clear()
        self._slices = Slices()
        # self._layers = Layers()

    def change_active_slice(self, slice_id):
        self._slices.set_active(slice_id)

    @property
    def active_slice(self):
        return self._slices.active

    """
    def change_active_layer(self, layer_id):
        self._layers.set_active(layer_id)
        
    def move_geom_obj_to_another_layer(self, layer_id, geom_id):
        self._layers.append([geom_id], layer_id)
    """

    def move_geoms_to_another_slice(self, slice_id, geom_id_list):
        self._slices.move_object(geom_id_list, slice_id)

    def get_all_geoms_at_slice(self, slice_id):
        return self._slices.get_object_ids_by_slice_id(slice_id)

    def get_slice_description(self, slice_id):
        return self._slices.get_slice_descr(slice_id)

    def change_slice_description(self, slice_id, new_discription):
        return self._slices.change_slice_descr(slice_id, new_discription)

    def get_all_slices(self):
        # в рамках одного слайса
        return self._slices.slice_id_list
