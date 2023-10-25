from copy import copy, deepcopy

from backend.GeomObject import WCS
from base.graph import BiGraph
from points.idgenerator import SimpleIDGenerator


class Slice:
    __slots__ = ["_cs", "_description"]

    def __init__(self, CS, description=""):
        self._cs = CS
        self._description = description

    @property
    def cs(self):
        return self._cs

    @property
    def description(self):
        return self._description

    def set_cs(self, new_cs):
        self._cs = new_cs

    def set_description(self, description_string):
        self._description = description_string


class iSlices(BiGraph):  # добавить словарь, как контейнер
    def add_slice(self, CS, description):
        pass

    def change_slice_cs(self, id_, new_cs):
        pass

    def change_slice_descr(self, id_, new_descr):
        pass

    def pop_slice(self, slice_id):
        pass

    def append(self, obj_id_list):
        pass

    def move_object(self, obj_id, new_slice_id):
        pass

    def delete_object(self, obj_id):
        pass

    def get_slice_id_by_obj_id(self, obj_id):
        pass

    def get_object_ids_by_slice_id(self, slice_id):
        pass

    def get_slice_neighbors_by_obj_id(self, obj_id):
        pass

    def get_slice_objects_dict(self):
        pass

    def slice_id_list(self):
        pass

    def is_exist(self, slice_id):
        pass

    def len(self):
        pass

    def is_active(self, slice_id):
        pass

    def set_active(self, slice_id):
        pass


class Slices(iSlices):

    def __init__(self):
        super().__init__()
        self._slices_dict = {-1: Slice(CS=WCS, description="")}
        self._id_generator = SimpleIDGenerator()
        self._active_id = -1
        self.add_red_v(-1)

    def add_slice(self, new_CS=WCS, new_description=""):
        #  new_CS - должна ли быть уникальной - ? проверять на совпадение с существующими - ?
        new_id = self._id_generator.new_id()
        if not self.has_red_v(new_id):
            self._slices_dict[new_id] = Slice(CS=new_CS, description=new_description)
            self.add_red_v(new_id)
            self._active_id = new_id  # новый слайс становится активным
            return new_id
        else:
            raise RuntimeError

    def add_by_id(self, id_, slise: Slice):
        if id_ not in self._slices_dict:
            self._slices_dict[id_] = slise

    def change_slice_cs(self, id_, new_cs):  # запретить?!
        if self.has_red_v(id_):
            self._slices_dict[id_].set_cs(new_cs)

    def get_slice(self, id_):
        if self.has_red_v(id_):
            return self._slices_dict[id_]
        else:
            return None

    def get_slice_descr(self, id_):
        if self.has_red_v(id_):
            return self._slices_dict[id_].description
        else:
            return ""

    def change_slice_descr(self, id_, new_descr):
        if self.has_red_v(id_):
            self._slices_dict[id_].set_description(new_descr)

    def pop_slice(self, id_):
        if self.has_red_v(id_) and id_ != -1:
            slice_obj = deepcopy(self._slices_dict[id_])
            obj_at_slice = copy(self.get_adj_list_red(id_))
            for obj_id in obj_at_slice:
                self.rem_red_blue_e([id_, obj_id])
                self.rem_blue_v(obj_id)
            self.rem_red_v(id_)
            if self._active_id == id_:
                self.set_active(-1)
            return slice_obj
        else:
            return None

    def append(self, obj_id_list):   # проверить на то, что элементы уже на нужном слое!
        active_slice_id = self.active
        for o_id in obj_id_list:
            if not self.has_blue_v(o_id):
                self.add_blue_v(o_id)
            old_slice_id = self.get_slice_id_by_obj_id(o_id)

            if old_slice_id is None:
                self.add_red_blue_e([active_slice_id, o_id])

            elif old_slice_id != active_slice_id:  # пока нет норм обработки ошибок, но нужно её как-то начинать
                # в таком случае нужна отмена операции, так как это перенос существующего объекта с другого слоя
                raise RuntimeError

    def move_object(self, obj_id, new_slice_id):
        if not self.has_blue_v(obj_id) or not self.has_red_v(new_slice_id):
            raise RuntimeError
        old_slice_id = self.get_slice_id_by_obj_id(obj_id)
        if old_slice_id is None:  # значит нечейный элемент
            raise RuntimeError
        else:
            if new_slice_id != old_slice_id:
                self.rem_red_blue_e([old_slice_id, obj_id])
                self.add_red_blue_e([new_slice_id, obj_id])

    def delete_object(self, obj_id):
        if self.has_blue_v(obj_id):
            layer_name = self.get_slice_id_by_obj_id(obj_id)
            if layer_name is not None:  # разрыв вязи
                self.rem_red_blue_e((layer_name, obj_id))
                self.rem_blue_v(obj_id)

    def get_slice_id_by_obj_id(self, obj_id):
        if self.has_blue_v(obj_id):
            ans = self.get_adj_list_blue(obj_id)
            return list(ans)[0] if ans else None
        else:
            return None

    def get_object_ids_by_slice_id(self, id_):
        if self.has_red_v(id_):
            return list(self.get_adj_list_red(id_))  # хотим лист на выходе
        else:
            return None

    def get_slice_objects_dict(self):
        s_o_dict = {}
        for slice_id in self.red_vertices:
            s_o_dict[slice_id] = self.get_adj_list_red(slice_id)
        return s_o_dict

    def get_slice_neighbors_by_obj_id(self, obj_id):
        if self.has_blue_v(obj_id):
            slice_id = self.get_slice_id_by_obj_id(obj_id)
            return self.get_object_ids_by_slice_id(slice_id)
        else:
            return None

    @property
    def slice_id_list(self):  # имена существующих слоёв
        return self.red_vertices

    def is_exist(self, id_):
        return True if self.has_red_v(id_) else False

    @property
    def active(self):
        return self._active_id

    def len(self):
        return len(self._slices_dict)

    def is_active(self, slice_id):
        return self._active_id == slice_id

    def set_active(self, slice_id):
        self._active_id = slice_id

    def are_the_same_slise(self,  obj_id_list):
        if obj_id_list:
            first_elem_id = obj_id_list[0]
            g_neigh_of_f_elem = self.get_slice_neighbors_by_obj_id(first_elem_id)
            for obg in obj_id_list[1:]:
                if obg not in g_neigh_of_f_elem:
                    return False
            return True
        else:
            raise RuntimeError


"""
s_c = Slices()
length = s_c.len()
ac_l = s_c.active
s_c.add_slice()
length2 = s_c.len()
ac_l2 = s_c.active
ll = s_c.slice_id_list

s_c.set_active(ll.pop(0))
ac_l3 = s_c.active
s_c.append([1, 2, 10])
s_c.move_object(1, ll.pop())
# s_c.remove_slice(ac_l3)
s_c.delete_object(2)  # 10 тоже удвлилась !
s_c.append([6, 3])
s_c.remove_slice(ac_l3)
"""
