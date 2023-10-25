from base.graph import BiGraph
from copy import copy


class IndexBase:
    def __init__(self):
        self.gen_index_base = BiGraph()
        self.local_index_base_dict = {}  # dict of BiGraphs/lists

    def _add_gen_connection(self, f_id, b_id):
        if not self.gen_index_base.has_red_v(f_id):
            self.gen_index_base.add_red_v(f_id)
        if not self.gen_index_base.has_blue_v(b_id):
            self.gen_index_base.add_blue_v(b_id)
        self.gen_index_base.add_red_blue_e((f_id, b_id))
        self.local_index_base_dict[(f_id, b_id)] = []

    def remove_gen_connection(self, f_id, b_id):
        if self.gen_index_base.has_red_blue_e((f_id, b_id)):
            self.gen_index_base.rem_red_blue_e((f_id, b_id))
            self._remove_inner_ids(f_id, b_id)

    @property
    def gen_ids_list(self):
        return copy(self.gen_index_base.edges)

    def get_front_ids_by_back(self, b_id):
        if self.gen_index_base.has_blue_v(b_id):
            return copy(self.gen_index_base.get_adj_list_blue(b_id))

    def get_back_id_by_front(self, f_id):
        if self.gen_index_base.has_red_v(f_id):
            b_id = self.gen_index_base.get_adj_list_red(f_id)
            if len(b_id):
                return copy(b_id).pop()
            else:
                return None

    def _set_inner_ids(self, f_id, b_id, inner_id_list):   # возможно переделать
        self.local_index_base_dict[(f_id, b_id)] = inner_id_list

    def insert_point_id(self, f_id, b_id, id_, pos):   # возможно переделать
        self.local_index_base_dict[(f_id, b_id)].insert(pos, id_)

    def set_point_id(self, f_id, b_id, new_id_fb_pair):
        if (f_id, b_id) in self.local_index_base_dict:
            inner_ids = self.local_index_base_dict[(f_id, b_id)]
            if inner_ids is not None and new_id_fb_pair[0] in inner_ids:
                inner_ids[new_id_fb_pair[0]] = new_id_fb_pair[1]

    def get_point_id(self, f_id, b_id, f_inner_id):  # f_inner_id - по факут индекс
        if (f_id, b_id) in self.local_index_base_dict:
            inner_ids = self.local_index_base_dict[(f_id, b_id)]
            if inner_ids is not None and f_inner_id < len(inner_ids):
                return inner_ids[f_inner_id]  # проверить!!
        return None

    def pop_point_id(self, f_id, b_id, f_inner_id):
        if (f_id, b_id) in self.local_index_base_dict:
            inner_ids = self.local_index_base_dict[(f_id, b_id)]
            if inner_ids is not None and f_inner_id < len(inner_ids):
                return inner_ids.pop(f_inner_id)  # проверить!!
        return None

    def add_new_record_fb(self, f_id, b_id, inner_id_list):
        self._add_gen_connection(f_id, b_id)
        self._set_inner_ids(f_id, b_id, inner_id_list)

    def _remove_inner_ids(self, f_id, b_id):
        if (f_id, b_id) in self.local_index_base_dict:
            self.local_index_base_dict.pop((f_id, b_id))

    def get_inner_ids(self, f_id, b_id):
        if (f_id, b_id) in self.local_index_base_dict:
            return copy(self.local_index_base_dict[(f_id, b_id)])

    def get_back_info_by_front(self, f_id, f_point_id):  # так как соответствие один ко многим
        b_id = self.get_back_id_by_front(f_id)  # всегда один элемент
        if b_id is not None:
            b_id = list(b_id)[0]
        else:
            return None, None
        if (f_id, b_id) in self.local_index_base_dict:
            pp = self.get_inner_ids(f_id, b_id)
            return (b_id, copy(pp[f_point_id])) if 0 <= f_point_id < len(pp) else (None, None)


"""
ib = IndexBase()

ib.add_gen_connection(1, 1)
ib.add_gen_connection(2, 1)
ib.set_inner_ids(1, 1, [0, 1, 2])
ib.set_inner_ids(2, 1, [3, 2, 4, 3])


ib = IndexBase()
ib.add_new_record_fb(1, 1, [0, 1, 2])
ib.add_new_record_fb(2, 1, [3, 2, 4, 3])
g = ib.gen_ids_list
d = ib.get_front_ids_by_back(1)
b_id = ib.get_back_id_by_front(2)
g_id, in_id = ib.get_back_info_by_front(2, 2)
ib.set_point_id(2, 1, (2, 14))
ib.remove_gen_connection(2, 1)
ib._remove_inner_ids(1, 1)
a = 1
"""
