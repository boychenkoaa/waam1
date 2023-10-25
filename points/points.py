from base.geom.raw.raw import add_pv, rotate
from points.IDEntity import IDEntity
from points.IDContainer import qFindPoint, mIDContainer
from points.Mediator import SmartMediator
from points.idgenerator import SimpleIDGenerator
from abc import abstractmethod, ABC
from points.CollisionDetector import mCollisionDetector


class PointID(IDEntity):
    def __init__(self, id_: int, point: tuple):
        super().__init__(id_, point)

    @property
    def point(self):
        return self.value


class iPoints(ABC):
    @abstractmethod
    def __init__(self):
        pass

    # должна вернуть id точки / найти ее
    @abstractmethod
    def add(self, point):
        pass

    @abstractmethod
    def __getitem__(self, id_):
        pass

    def __setitem__(self, id_, new_point: tuple):
        pass

    @abstractmethod
    def __contains__(self, point: tuple):
        pass

    @abstractmethod
    def rem(self, id_: int):
        pass

    @abstractmethod
    def move(self, id_, point_new_coord: tuple):
        pass

    @abstractmethod
    def move_all(self, vector: tuple):
        pass

    @abstractmethod
    def find(self, point: tuple):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def id_list(self):
        pass

    @abstractmethod
    def p_list(self):
        pass

    def rotate(self, rotation_center, angle):
        pass


class SimplePoints(iPoints):  # возможно удалить медиатор
    __slots__ = ["_container", "_id_generator", "_detector", "_all_unique"]

    def __init__(self, point_list: list = None):
        super().__init__()
        if point_list is None:
            point_list = []
        self._container = mIDContainer()
        self._id_generator = SimpleIDGenerator()
        self._detector = qFindPoint(self._container, epsilon=1e-6)
        self._all_unique = True
        for point in point_list:
            self.add(point)

    def add(self, point):
        assert not (point in self)
        new_id = self._id_generator.new_id()
        self._container.add(PointID(new_id, point))
        return new_id

    def __getitem__(self, id_):
        return self._container[id_]

    def __setitem__(self, id_, new_point: tuple):
        self._container[id_] = new_point

    def __contains__(self, point: tuple):
        return self._detector.contains(point)

    def find(self, point: tuple):
        return self._detector.get(point)

    def rem(self, id_: int):
        self._container.rem(id_)

    def __iter__(self):
        return self._container.__iter__()

    def __len__(self):
        return len(self._container)

    def p_list(self):
        return [p_id.point for p_id in self]

    def id_list(self):
        return [p_id.id for p_id in self]

    def __str__(self):
        ans = ""
        for id, co in self:
            ans += "id = {}; co = {}\n".format(id, co)
        return ans

    def __repr__(self):
        return self.__str__()


class cAddOrFindPoints:
    def __init__(self, points: iPoints):
        self._points = points

    def do(self, point: tuple):
        return self._points.find(point)


class SmartPoints(iPoints):
    """
    Класс хранения точек с возможностью проверки их уникальности,
    использует вспомогательные классы collision detector и mediator.
    """
    __slots__ = ["_container", "_id_generator", "_collision_detector", "_mediator"]

    def __init__(self, point_list: list = None):
        super().__init__()
        if point_list is None:
            point_list = []
        self._container = mIDContainer()
        self._id_generator = SimpleIDGenerator()
        self._collision_detector = mCollisionDetector()
        self._mediator = SmartMediator(self._container, self._collision_detector)
        for point in point_list:
            self.add(point)

    def add(self, point):
        find_point = self.find(point)
        if find_point is None:  # тут проверить find возвращает None!!
            new_id = self._id_generator.new_id()
            self._container.add(IDEntity(new_id, point))
        else:
            # найти по индексу в collision detector id в container
            new_id = find_point  # сейчас id и индекс никак не связаны
        return new_id

    def add_by_id(self, new_id, point):  # протестировать!!!
        assert self[new_id] is None
        assert self.find(point) is None
        self._container.add(IDEntity(new_id, point))

    def find(self, point: tuple):
        return self._collision_detector.find(point)

    def get_sort_points(self):  # сортировка по (x, y)
        return self._collision_detector.get_sorted_points()

    def __getitem__(self, id_):
        return self._container[id_] if id_ in self._container else None

    def __setitem__(self, id_, new_point: tuple):  # проверить
        self._container[id_] = new_point

    def __contains__(self, point: tuple):
        return False if self.find(point) is None else True

    def rem(self, id_: int):  # доделать синхронизацию с collision detector
        self._container.rem(id_)

    def rem_p(self, point):
        id_ = self.find(point)
        if id_:
            self._container.rem(id_)

    def move(self, id_, point_new_coord: tuple):
        assert self[id_] is not None
        self._container[id_] = point_new_coord

    def move_all(self, vector: tuple):  # проверить
        for id_ in self.id_list():
            old_coord = self[id_].value
            new_coord = add_pv(old_coord, vector)
            self.move(id_, new_coord)

    def rotate(self, rotation_center: tuple, angle: float):
        for id_ in self.id_list():
            old_coord = self[id_].value
            new_coord = rotate(old_coord, rotation_center, angle)
            self.move(id_, new_coord)

    def p_list(self):
        return [p_id.value for p_id in self]

    def id_list(self):
        return [p_id.id for p_id in self]

    def raw(self):  # проверить!!
        return [(p_id.id, p_id.value) for p_id in self]

    def __iter__(self):
        return self._container.__iter__()

    def __len__(self):
        return len(self._container)

    def __repr__(self):
        return super().__repr__()

"""
smart_point_list = SmartPoints()
smart_point_list.add((5, 6))
smart_point_list.add((3, 6))
smart_point_list.add((5, 6))
smart_point_list.add((3, 6))
a = smart_point_list.find((3, 6))
b = smart_point_list.find((3, 5))
c = smart_point_list.find((5, 6))
n = smart_point_list[c]
v = smart_point_list[5]
# point_list.rem(a)
# point_list.rem(c)
it = smart_point_list.__iter__()
for p in smart_point_list:
    print(p.id)
"""



