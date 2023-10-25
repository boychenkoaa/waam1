from sortedcontainers import SortedKeyList
from base.geom.raw.raw import distance_pp
from points.Mediator import BaseMediatorClient, SmartMediator
from points.IDEntity import IDEntity


class iIDContainer:
    def __init__(self):
        pass

    def __contains__(self, id_):
        pass

    def __getitem__(self, id_):
        pass

    def __setitem__(self, id_, value):
        pass

    def add(self, id_entity: IDEntity):
        pass

    def rem(self, id_):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def is_empty(self):
        pass

    def __repr__(self):
        pass

    def __clear__(self):
        pass


class qFindPoint:
    __slots__ = ["_container", "_epsilon"]

    def __init__(self, container: iIDContainer, epsilon: float = 1e-6):
        self._container = container
        self._epsilon = epsilon

    def get(self, point):
        for point_id in self._container:
            if distance_pp(point_id.value, point) < self._epsilon:
                return point_id.id
        return None

    def contains(self, point):
        return not (self.get(point) is None)


class SimpleContainer(iIDContainer):
    __slots__ = ["_id_list"]

    def __init__(self):
        super().__init__()
        self._id_list = {}  # list of identity

    def is_empty(self):
        return len(self._id_list) == 0

    def __contains__(self, id_):
        return not (self._id_list[id_] is None)

    def __len__(self):
        return len(self._id_list)

    def __getitem__(self, id_):
        return self._id_list[id_]


class IDContainer(iIDContainer):
    __slots__ = ["_skl"]

    def __init__(self):
        super().__init__()
        self._skl = SortedKeyList(key=self._func_id)  # key=lambda id_entity: id_entity.id

    @staticmethod
    def _func_id(id_entity):
        return id_entity.id

    def _bkl(self, id_):
        return self._skl.bisect_key_left(id_)

    def is_empty(self):
        return len(self._skl) == 0

    def _raw_index(self, id_):
        if len(self) == 0:
            return None

        ans = self._bkl(id_)
        if 0 <= ans < len(self._skl):
            if self._skl[ans].id == id_:
                return ans
        return None

    def find_by_id(self, id_):
        ind = self._raw_index(id_)
        return ind

    def __contains__(self, id_):
        return not (self._raw_index(id_) is None)

    def __len__(self):
        return len(self._skl)

    def __getitem__(self, id_):
        raw_idx = self._raw_index(id_)
        assert not (raw_idx is None)
        return self._skl[raw_idx]

    def __setitem__(self, id_, value):
        self[id_].set_value(value)

    def rem(self, id_):
        assert id_ in self
        ind = self._raw_index(id_)
        # путь возвращает точку, хуже никому не будет от этого
        return self._skl.pop(ind)

    def add(self, id_entity: IDEntity):
        assert not (id_entity.id in self)
        assert hasattr(id_entity, "id")
        self._skl.add(id_entity)

    def __repr__(self):
        if self.is_empty():
            return "Empty IDContainer"
        ans = ""
        for id_entity in self._skl:
            ans += str(id_entity) + '\n'
        return ans

    def __iter__(self):
        return iter(self._skl)

    def clear(self):
        self._skl.clear()

    # обращение, как к массиву
    def get(self, ind):
        return self._skl[ind]

    def pop(self, ind=0):
        return self._skl.pop(ind)


class mIDContainer(IDContainer, BaseMediatorClient):

    def __init__(self):
        IDContainer.__init__(self)
        BaseMediatorClient.__init__(self)

    def add(self, point: IDEntity):
        assert isinstance(self._mediator, SmartMediator)
        super().add(point)
        self._mediator.add_point(point)

    def rem(self, id_):
        assert isinstance(self._mediator, SmartMediator)
        point = super().rem(id_)
        self._mediator.remove(point.value)

