# на группы пока забьем
from copy import deepcopy

from base.graph import BiGraph
from points.idgenerator import SimpleIDGenerator


class iGroupContainer(BiGraph):
    def create_empty(self, new_g_id):
        pass

    def disband(self, g_id):
        pass

    def append(self, g_id, obj_id_list):
        pass

    def get_group_id_by_obj_id(self, obj_id):
        pass

    def get_object_ids_by_g_id(self, g_id):
        pass

    def get_group_objects_dict(self):
        pass

    def group_list(self):
        pass

    def is_exist(self, g_id):
        pass


# скорее всего будет ещё один коллега, который будет общаться с GroupContainer и со Storage
class GroupContainer(iGroupContainer):  # g_id - red, objects - blue

    def __init__(self):
        super().__init__()

    def get_group_id_by_obj_id(self, obj_id):
        if self.has_blue_v(obj_id):
            ans = self.get_adj_list_blue(obj_id)
            return list(ans)[0] if ans else None
        else:
            return None

    def get_object_ids_by_g_id(self, g_id):
        if self.has_red_v(g_id):
            return list(self.get_adj_list_red(g_id))  # хотим лист на выходе
        else:
            return None

    def get_group_objects_dict(self):
        g_o_dict = {}
        for group in self.red_vertices:
            g_o_dict[group] = self.get_adj_list_red(group)
        return g_o_dict

    def get_group_neighbors_by_obj_id(self, obj_id):
        if self.has_blue_v(obj_id):
            g_id = self.get_group_id_by_obj_id(obj_id)
            return self.get_object_ids_by_g_id(g_id)
        else:
            return None

    @property
    def group_list(self):
        return self.red_vertices

    def is_exist(self, g_id):
        return True if self.has_red_v(g_id) else False

    def create_empty(self, new_g_id):
        self.add_red_v(new_g_id)
        return new_g_id

    def add_by_id(self, g_id, obj_id_list):  # проверить, восстановление ранее существующей группы
        self.add_red_v(g_id)
        self.add_blue_vertices(obj_id_list)
        for obj_id in obj_id_list:
            self.add_red_blue_e([g_id, obj_id])

    def disband(self, g_id):
        if self.has_red_v(g_id):
            adj_list = deepcopy(self.get_adj_list_red(g_id))
            for obj_id in adj_list:
                self.rem_red_blue_e((g_id, obj_id))
                self.rem_blue_v(obj_id)
        self.rem_red_v(g_id)

    def append(self, g_id, obj_id_list):  # ограничения!!
        # проверить нен ли в других группах, если есть, то расформировывать
        if self.has_red_v(g_id):
            self.add_blue_vertices(obj_id_list)
            for obj_id in obj_id_list:
                self.add_red_blue_e([g_id, obj_id])

    def remove(self, g_id, obj_id_list):  # для отмены добавления в команде
        if self.has_red_v(g_id):
            for o_id in obj_id_list:
                current_g_id = self.get_group_id_by_obj_id(o_id)
                if current_g_id == g_id:
                    self.rem_red_blue_e([g_id, o_id])
                    self.rem_blue_v(o_id)
                else:
                    raise RuntimeError

"""
a = GroupContainer()
new_g_id = a.create_empty()
a.append(new_g_id, [1, 2, 3])
a.append(new_g_id, [100500])
g_n = a.get_group_neighbors_by_obj_id(6)
second_g_id = a.create_empty()
a.append(second_g_id, [1, 2, 6])
a.remove(second_g_id, [1, 2])
# g_n = a.get_group_neighbors_by_obj_id(6)
b = 0
"""