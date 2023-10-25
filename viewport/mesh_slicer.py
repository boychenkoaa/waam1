from base.geom.raw.raw import distance_pp, EPSILON, EPSILON2

class SimpleStorage:
    def __init__(self):
        self._storage = {}
        self._last_id = 0

    def has_id(self, id_):
        return id_ in self._pt_dict.keys()

    @property
    def last_id(self):
        return self._last_id

    def _new_id(self):
        self._last_id += 1
        return self._last_id

    def __contains__(self, id_):
        return self.has_id(id_)

    def find_value(self, value):
        for key, val in self._storage.items():
            if val == value:
                return key
        return None

    def __getitem__(self, id_: int):
        assert id_ in self
        return self._pt_dict[id]

    def __setitem__(self, id_: int, new_value):
        assert id_ in self
        self._storage.update({id_: new_value})

    def add_value(self, new_value):
        self._storage.update({self._new_id(): new_value})
        return self.last_id

    def pop(self, id_, chenk_in=False):
        f = id_ in self
        if check_in:
            assert f
        if f:
            return self._storage.pop(id_)
        return None

"""
# оберточка над словарем с id-ключами и поиском с точностью до эпсилон
class SimplePointStorage(SimpleStorage):
    def __init__(self):
        super().__init__()

    def find_pt(self, point):
        for vert_id, pt in self._verts.items():
            if distance_pp(point, pt) < EPSILON:
                return vert_id
        return None

    def has_pt(selfself, point: tuple):
        return not self.find_pt is None

    def add_pt(self, point):
        return self.add_value(point)

    def __str__(self):
        return str(self._pt_dict)

    def __repr__(self):
        return str(self)


def sort_tuple(t: tuple):
    return tuple(sorted(t))

# verts - обертка над точками
# edges и faces - обычные множества кортежей
# кортежи добавляются строго в порядке неубывания id-вершин
class SimpleMesh:
    def __init__(self, pt_list):
        self._verts = SimplePointStorage(pt_list)
        self._edges = set()
        self._faces = set()

    def has_vert(self, vert_id):
        return self._verts.has_id(vert_id)

    def has_pt(self, point: tuple):
        return self._verts.has_pt(point)

    def find_pt(self, point: tuple):
        return self._verts.find_pt(point)

    def add_vert(self, point: tuple):
        return self._verts.add_pt(point)

    def has_edge(self, edge: tuple):
        return sort_tuple(edge) in self._edges

    def add_edge(self, edge: tuple, alarm_if_exist=False):
        assert edge[0] != edge[1]
        assert self.has_vert(edge[0])
        assert self.has_vert(edge[1])
        assert not (alarm_if_exist and self.has_edge(edge))
        if not self.has_edge(edge):
            self._edges.add(sort_tuple(edge))

    def has_face(self, face: tuple):
        return sort_tuple(face) in self._faces

    def add_face(self, face: tuple, alarm_if_exist=False):
        face_sorted = sort_tuple(face)
        assert face[0] != face[1] and face[1] != face[2] and face[2] != face[0]
        assert not(alarm_if_exist and self.has_face(face_sorted))
        assert face[0] in self._verts
        assert face[1] in self._verts
        assert face[2] in self._verts

        ed01 = (face[0], face[1])
        ed12 = (face[1], face[2])
        ed02 = (face[0], face[2])
        self.add_edge(ed01, alarm_if_exist=False)
        self.add_edge(ed02, alarm_if_exist=False)
        self.add_edge(ed12, alarm_if_exist=False)
        self._faces.add(face_sorted)

    def has_segment(self, segment: tuple):
        v0 = self.find_pt(segment[0])
        v1 = self.find_pt(segment[1])
        if v1 is None or v0 is None:
            return False
        return self.has_edge((v0, v1))
"""

