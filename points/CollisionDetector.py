from sortedcontainers import SortedKeyList
from base.geom.raw.raw import distance_pp, EPSILON, int_approximate
from points.IDEntity import IDEntity
from points.Mediator import BaseMediatorClient
from copy import copy

default_eps = EPSILON


class imCollisionDetector:

    def __contains__(self, point):
        pass

    def insert(self, id_entity):
        pass

    def remove(self, point):
        pass


class CollisionDetector(imCollisionDetector):
    def __init__(self, def_eps=default_eps):  # где задаём - ?
        self.__point_tree = SortedKeyList(key=self.key_func)  # key=lambda id_entity: self.__approximate(id_entity.value)
        self.eps = def_eps

    def key_func(self, id_entity):
        return self.__approximate(id_entity.value)

    def __bkl(self, point: tuple):
        ans = self.__point_tree.bisect_key_left(self.__approximate(point))
        return ans

    def __raw_index(self, point: tuple):
        point_count = len(self)
        if point_count == 0:
            return None
        ans = self.__bkl(point)
        if 0 <= ans <= point_count:
            if ans < point_count and distance_pp(self.__point_tree[ans].value, point) < self.eps:
                return ans
            if ans > 0 and distance_pp(self.__point_tree[ans-1].value, point) < self.eps:
                return ans - 1
        return None

    def __approximate(self, value: tuple):
        return (int_approximate(copy(value[0])), int_approximate(copy(value[1])))

    def find(self, point: tuple):
        if self.__contains__(point):
            p_ind = self.__raw_index(point)
            ans = self.__point_tree[p_ind].id
        else:
            ans = None
        return ans  # возвращаем id

    def insert(self, point: IDEntity):
        self.__point_tree.add(point)

    def remove(self, point: tuple):
        p_ind = self.__raw_index(point)
        if p_ind:
            self.__point_tree.pop(p_ind)

    def get_sorted_points(self):
        return [x.value for x in self.__point_tree]

    def __contains__(self, point: tuple):
        ans = False
        ind = self.__raw_index(point)
        if ind is not None:
            ans = True
        return ans

    def __len__(self):
        return len(self.__point_tree)


class mCollisionDetector(CollisionDetector, BaseMediatorClient):

    def __init__(self):
        CollisionDetector.__init__(self)
        BaseMediatorClient.__init__(self)

