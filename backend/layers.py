# на группы пока забьем
from copy import deepcopy, copy

from backend.GeomObject import DPlineP
from base.graph import BiGraph
from points.IDContainer import IDContainer
from points.idgenerator import SimpleIDGenerator


# слой defaut нельзя удалить, должен быть всегда хотя бы один слой
class Layer:
    __slots__ = ["_dp", "_visible", "_frozen"]

    def __init__(self, DP, is_visible=True, is_frozen=False):
        # self._name = new_name  # убрать
        self._dp = DP
        self._visible = is_visible
        self._frozen = is_frozen

    @property
    def dp(self):
        return self._dp

    @property
    def is_visible(self):
        return self._visible

    @property
    def is_frozen(self):
        return self._frozen

    def set_dp(self, new_dp):
        self._dp = new_dp

    def set_visible_state(self, is_visible):
        self._visible = is_visible

    def set_frozen_state(self, is_frozen):
        self._frozen = is_frozen


class iLayers(BiGraph):  # добавить словарь, как контейнер
    def add_layer(self, name=None, DP=None, is_visible=True, is_frozen=False):  #  DP - default ?!
        pass

    def remove_layer(self, name):
        pass

    def rename_layer(self, old_name, new_name):
        pass

    def is_empty(self, name):
        pass

    def append(self, name, obj_id_list):
        pass

    def get_layer_name_by_obj_id(self, obj_id):
        pass

    def get_object_ids_by_layer_name(self, name):
        pass

    def get_layer_neighbors_by_obj_id(self, obj_id):
        pass

    def get_layer_objects_dict(self):
        pass

    def delete_objects(self, obj_id_list):
        pass

    def len(self):
        pass

    def layer_list(self):
        pass

    def is_exist(self, name):
        pass

    def is_active(self, layer_name):
        pass

    def set_active(self, layer_name):
        pass


class Layers(iLayers):

    def __init__(self):
        super().__init__()
        self._layers_dict = {"default": Layer(DP=DPlineP, is_visible=True, is_frozen=False)}  # DP=DPlineP - поменять!
        self._id_generator = SimpleIDGenerator()
        self._active_name = "default"
        self.add_red_v("default")
        self._id_generator.new_id()  # прокрутка id

    def __getitem__(self, layer_name):  # как сделать приватным ?
        if self.has_red_v(layer_name):
            return self._layers_dict[layer_name]
        else:
            return None  # по хорошему должна быть ошибка

    def rename_layer(self, old_name, new_name):  # делать подмену!
        if self.has_red_v(old_name) and old_name != "default" and not self.has_red_v(new_name):
            self._layers_dict[new_name] = self._layers_dict.pop(old_name)
            self.add_red_v(new_name)
            neigh = copy(self.get_adj_list_red(old_name))
            for nei in neigh:
                self.rem_red_blue_e((old_name, nei))
                self.add_red_blue_e((new_name, nei))
            self.rem_red_v(old_name)
            if self.active == old_name:
                self.set_active(new_name)

    def get_layer_name_by_obj_id(self, obj_id):
        if self.has_blue_v(obj_id):
            ans = self.get_adj_list_blue(obj_id)
            return list(ans)[0] if ans else None
        else:
            return None

    def get_object_ids_by_layer_name(self, name):
        if self.has_red_v(name):
            return list(self.get_adj_list_red(name))  # хотим лист на выходе
        else:
            return None

    def get_layer_objects_dict(self):
        l_o_dict = {}
        for layer in self.red_vertices:
            l_o_dict[layer] = self.get_adj_list_red(layer)
        return l_o_dict

    def get_layer_neighbors_by_obj_id(self, obj_id):
        if self.has_blue_v(obj_id):
            layer_name = self.get_layer_name_by_obj_id(obj_id)
            return self.get_object_ids_by_layer_name(layer_name)
        else:
            return None

    @property
    def active(self):
        return self._active_name

    @property
    def layer_list(self):  # имена существующих слоёв
        return self.red_vertices

    def len(self):
        return len(self._layers_dict)

    def is_exist(self, name):
        return True if self.has_red_v(name) else False

    def is_active(self, layer_name):
        return self._active_name == layer_name

    def add_layer(self, name=None, is_visible=True, is_frozen=False, dp=None):
        if not self.has_red_v(name):
            if dp is None:
                dp = DPlineP
            if name is None:  # получаем уникальное имя
                new_name = "new layer " + str(self._id_generator.new_id())
                while self.has_red_v(new_name):
                    new_name = "new layer " + str(self._id_generator.new_id())
                name = new_name  # получили уникальное имя
            self._layers_dict[name] = Layer(dp, is_visible, is_frozen)  # добавили объект слоя
            self.add_red_v(name)

    def remove_layer(self, name):
        if self.has_red_v(name) and not self.get_adj_list_red(name) and name != "default":
            self.rem_red_v(name)
            if self.active == name:
                self.set_active("default")

    def append(self, obj_id_list, name=None):   # проверить на то, что элементы уже на нужном слое!
        # тут нужно именно перести с другого слоя на новый, или со слоёв - ?
        if name is None:
            name = self._active_name
        if self.has_red_v(name):  # если слой уже есть, проверять на активность?
            for o_id in obj_id_list:
                if not self.has_blue_v(o_id):
                    self.add_blue_v(o_id)
                old_layer_name = self.get_layer_name_by_obj_id(o_id)
                if old_layer_name is not None:  # разрыв старой связи
                    self.rem_red_blue_e((old_layer_name, o_id))
                self.add_red_blue_e([name, o_id])

    def delete_objects(self, obj_id_list):
        for o_id in obj_id_list:
            if self.has_blue_v(o_id):
                layer_name = self.get_layer_name_by_obj_id(o_id)
                if layer_name is not None:  # разрыв вязи
                    self.rem_red_blue_e((layer_name, o_id))
                    self.rem_blue_v(o_id)

    def set_active(self, layer_name):
        self._active_name = layer_name


"""
синхронизация с внутренностью геом объекта будет выше 
l_c = Layers()
length = l_c.len()
ac_l = l_c.active
l_c.add_layer()
length2 = l_c.len()
ac_l2 = l_c.active
ll = l_c.layer_list
l_c.set_active(ll.pop(0))
ac_l3 = l_c.active
l_c.append(ac_l3, [1, 2, 10])
l_c.rename_layer('new layer 1', 'my_name')
# l_c.remove_layer(ac_l3)
l_c.delete_objects([2])
l_c.append(ll[0], [1, 10])
l_c.remove_layer(ac_l3)
b = 0
"""

