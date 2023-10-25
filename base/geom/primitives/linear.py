from copy import copy, deepcopy

# from base.geom.geomgraph import GeomGraph
from points.points import iPoints, SmartPoints
import sortedcontainers
from enum import Enum, IntEnum
import shapely.geometry

eps = 0.0000001
alfa = 0.00001


# список индексов элемента в списке
def indices(elem, list_):
    ans = []
    for i in range(len(list_)):
        if list_[i] == elem:
            ans.append(i)
    return ans


def det(x1, y1, x2, y2, x3, y3):
    return (x2 - x1)*(y3 - y1) - (y2 - y1)*(x3 - x1)


class VectorDirection(Enum):
    WAY_UP = 1
    WAY_DOWN = 2
    HORIZONTALLY = 3


class BypasDirection(IntEnum):
    CW = 1
    CCW = 2


def get_x(edge, y):
    if abs(edge[0][1] - edge[1][1]) < eps:
        return edge[1][0]
    return edge[0][0] + (edge[1][0] - edge[0][0]) * (y - edge[0][1]) / (edge[1][1] - edge[0][1])


def edge_direction(edge):
    """
    edge is considered as a vector
    compare by y-coordinate
    with epsilon precision
    """
    begin = edge[0]
    end = edge[1]
    if begin[1] - end[1] > eps:
        return VectorDirection.WAY_DOWN
    elif end[1] - begin[1] > eps:
        return VectorDirection.WAY_UP
    else:
        return VectorDirection.HORIZONTALLY


def cut_edge_on_epsilon(edge, at_head):  # получаем на вход точки
    """
    edge - the edge we want to shorten
    at_head = True or False, if the flag is true, then we cut off the head of the vector
    """
    if not at_head:  # если отрезаем с другого конца, просто меняем местами начало и конец ребра
        edge = (edge[1], edge[0])

    begin_coord = edge[0]
    end_coord = edge[1]

    direction = edge_direction(edge)
    if direction == VectorDirection.WAY_UP:
        # если конец по y, выше, чем начало ребра, следовательно, y-координату конца уменьшаем на эпс.
        new_y_coord = end_coord[1] - alfa
    elif direction == VectorDirection.WAY_DOWN:
        new_y_coord = end_coord[1] + alfa
    else:
        # если ребро горизонтальное, то новой точки нет
        if at_head:
            ed_by_id = (edge[0], edge[1])
        else:
            ed_by_id = (edge[1], edge[0])  # обратное инвертирование
        point_id = edge[1]
        return point_id, ed_by_id

    new_x_coord = get_x((begin_coord, end_coord), new_y_coord)
    cut_edge_coord = (begin_coord, (new_x_coord, new_y_coord))

    if at_head:
        ed_by_id = (edge[0], cut_edge_coord[1])
    else:
        ed_by_id = (cut_edge_coord[1], edge[0])
    return cut_edge_coord[1], ed_by_id


# iGeom - любая геометрия, включающая точки (как множество, с детектором и прочим)
# от нее наследуются и
# прописывание SimplePoints в конструкторе позволяет самому выбирать тип точек
# ? - сделать наследников для каждого конкретного набора точек - ?


class iGeom:
    __slots__ = ["_points"]

    def __init__(self, points: iPoints):
        self._points = points

    def insert(self, index: int, point: tuple):
        pass

    def points(self):
        pass

    def segments(self):
        pass

    def id_list(self):
        pass

    def __getitem__(self, index):
        pass

    def find(self, point: tuple):
        pass

    def pop(self, index: int):
        pass

    def move_all(self, vector: tuple):
        pass

    def __setitem__(self, id_, new_point: tuple):
        pass

    def __len__(self):
        pass

    def __iter__(self):
        pass


# точка может повторяться дваждый под одним id в разных позициях
# на этом уровне самопересечения допускаются
# хранит

class PointChain(iGeom):  # проверить
    __slots__ = ["_points", "_li"]  # _points - дублируются с базовым классом

    def __init__(self, list_xy: list = None):
        super().__init__(SmartPoints())
        self._li = []
        # проверить
        for index, point in enumerate(list_xy):  # точки могут повторяться
            new_id = self._points.add(point)
            self._li.insert(index, new_id)

    def convert_to_shapely(self):
        # набор точек шейпли
        return list(map(lambda point: shapely.geometry.Point(point), self.points()))

    def revers(self):
        self._li.reverse()

    @property
    def raw(self):
        return copy(self._li)

    def __len__(self):
        return len(self._li)

    # переделать в getitem
    def p(self, id_):  # точка по id
        return self._points[id_].value

    def i(self, index):  # id точки находящейся по данному индексу
        return self._li[index]

    def __getitem__(self, ind):  # возвращаем координаты точки по index
        return self._points[self.i(ind)].value

    def __setitem__(self, id_, new_point: tuple):
        self._points[id_] = new_point

    def __contains__(self, point):  # есть ли точка с такой координатой
        return point in self._points

    # переделать !!
    def has_id(self, id_):  # есть ли такой id
        return True if self.i(id_) else False

    # удаление с возвратом значения по индексу
    def pop(self, index):
        pop_id = self._li.pop(index)
        if pop_id not in self._li:  # если больше точек с таким индексом нет, то удаляем из хранилища точек
            self._points.rem(pop_id)
        return pop_id

    def rem_id(self, id_):
        self._li = list(filter(lambda x: x != id_, self._li))
        self._points.rem(id_)

    def rem_all_p(self, point):
        id_ = self.find(point)
        if id_ is not None:
            self.rem_id(id_)

    def find(self, point):  # возвращаем id точки
        return self._points.find(point)

    def insert(self, index: int, point: tuple = None):  # добавление точки по индексу в списке
        if point is None:  # вычисляем центр отрезка
            point_x = (self[index - 1][0] + self[index][0])/2
            point_y = (self[index - 1][1] + self[index][1])/2
            point = (point_x, point_y)
        new_id = self._points.add(point)
        self._li.insert(index, new_id)
        return new_id

    """        """
    def append(self, point: tuple):
        new_id = self._points.add(point)
        self._li.append(new_id)
        return new_id

    def move_id(self, id_, new_coord: tuple):
        self._points.move(id_, new_coord)

    def move(self, index, new_coord: tuple):
        if len(self.all_index_id(self.i(index))) > 1:
            # создаём новую координату
            new_id = self._points.add(new_coord)
            self._li[index] = new_id
        else:
            self._points.move(self.i(index), new_coord)

    def move_all(self, vector: tuple):
        self._points.move_all(vector)

    def rotate(self, rotation_center: tuple, angle: float):
        self._points.rotate(rotation_center, angle)

    # индекс первого вхождения точки
    def index_p(self, point):
        id_ = self.find(point)
        return self.index_id(id_) if id_ is not None else False  # или None?

    # индекс первого вхождения точки по id
    def index_id(self, id_):
        return self._li.index(id_) if id_ in self._li else False

    # хотим по id точки получать все индексы
    def all_index_id(self, id_):
        return [i for i, x in enumerate(self._li) if x == id_]

    # хотим по точке получать все индексы
    def all_index_p(self, point):
        id_ = self.find(point)
        return self.all_index_id(id_) if id_ is not None else False

    # проверка на самопересечение
    def self_intersect(self):
        # если индексов больше, то есть самопересечения
        return True if len(self) != len(self._points) else False

    def validate(self):  # для чего?
        pass

    def segments(self):
        pass

    def points(self):
        return [self.p(id_) for id_ in self._li]

    def __str__(self):
        return str(self._li)

    def __repr__(self):
        return self.__str__()


# контур
class Contour(PointChain):
    __slots__ = ["_bypas"]  # "_points", "_li",

    def __init__(self, list_xy: list):
        super().__init__(list_xy)
        if self.check_cw_bypas() is True:
            self._bypas = BypasDirection.CW
        else:
            self._bypas = BypasDirection.CCW

    @property
    def type(self):
        return "Contour"

    def convert_to_shapely(self, boundary=False):
        return shapely.geometry.Polygon(self.points()).boundary if boundary else shapely.geometry.Polygon(self.points())

    def check_cw_bypas(self):  # проверить!
        min_x_point = self[0]
        min_ind = 0
        for i in range(len(self) - 1):
            if self[i] < min_x_point:
                min_x_point = self[i]
                min_ind = i
        return True if det(self[min_ind][0], self[min_ind][1], self[min_ind-1][0], self[min_ind-1][1], self[min_ind+1][0], self[min_ind+1][1]) > 0 else False

    def revers(self):
        super().revers()
        # проверить!
        self._bypas = BypasDirection.CCW if self._bypas is BypasDirection.CW else BypasDirection.CW

    def set_bypas(self, bypas_direction):  # проверить!
        if self._bypas != bypas_direction:
            # хотим переписать контур, так чтобы обход был в другую сторону
            self.revers()
        return self

    def segments(self, bypas_direction=None):
        if bypas_direction is None or bypas_direction == self._bypas:
            # проверить!
            ans = [[self[i], self[(i + 1) % len(self)]] for i in range(len(self))] # [[self[i - 1], self[i]] for i in range(len(self))]
        else:
            ans = [(self[i], self[i - 1]) for i in range(len(self) - 1, -1, -1)]
        return ans

    def points(self, bypas_direction=None):
        if bypas_direction is None or bypas_direction == self._bypas:
            pnts = [self[i] for i in range(len(self))]
            pnts.append(self[0])
        else:
            pnts = [self[i] for i in range(len(self) - 1, -1, -1)]
            pnts.append(self[len(self) - 1])
        return pnts

    def leftmost_edge(self, bypas_direction):
        """
        Возвращает ребро, которое идёт в левейшую (нижнюю) точку
        """
        contour_bypas_cw = self.points(bypas_direction)
        c_leftmost_point = contour_bypas_cw[0]
        c_leftmost_edge = (contour_bypas_cw[-1], contour_bypas_cw[0])
        for i in range(1, len(contour_bypas_cw)):
            if (contour_bypas_cw[i][0] < c_leftmost_point[0]) or (contour_bypas_cw[i][0] == c_leftmost_point[0]) and (
                    contour_bypas_cw[i][1] < c_leftmost_point[1]):
                c_leftmost_point = contour_bypas_cw[i]
                c_leftmost_edge = (contour_bypas_cw[i - 1], contour_bypas_cw[i])
        return c_leftmost_edge

    def __getitem__(self, index):
        return super().__getitem__(index)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self._li)


# ломаная, что добавить - ?

class PLine(PointChain):
    # переделать
    def segments(self):
        return [[self[ind], self[ind + 1]] for ind in range(len(self) - 1)]

    def convert_to_shapely(self):
        return shapely.geometry.LineString(self.points())

    @property
    def type(self):
        return "PLine"


# контур + дырки
class Polygon:
    __slots__ = ["contour", "holes"]

    def __init__(self, contour: list, holes: list):  # проверить
        self.contour = Contour(contour).set_bypas(BypasDirection.CW)  # список координат
        if holes is not None:
            self.holes = [Contour(hole).set_bypas(BypasDirection.CCW) for hole in holes]  # список списков координат

    @property
    def type(self):
        return "Polygon"

    def get_all_contours(self):
        contour_list = [deepcopy(self.contour)]
        for hole in self.holes:
            contour_list.append(deepcopy(hole))
        return contour_list

    def convert_to_shapely(self):
        shap_holes = []
        for hole in self.holes:
            shap_holes.append(hole.points())
        return shapely.geometry.Polygon(self.contour.points(), shap_holes)

    def __setitem__(self, id_, value):  # id_: tuple
        current_contour = self.contour if id_[0] == 0 else self.holes[id_[0] - 1]
        current_contour[id_[1]] = value

    # координата по индексному id_
    def __getitem__(self, ind_: tuple):  # id_ = (id контура, ind точки)
        point = self.contour[ind_[1]] if ind_[0] == 0 else self.holes[ind_[0] - 1][ind_[1]]
        return point

    def p(self, id_: tuple):  # id_ = (id контура, id точки)
        point = self.contour.p(id_[1]) if id_[0] == 0 else self.holes[id_[0] - 1].p(id_[1])
        return point

    def find(self, point: tuple):  # список id? добавить break, как только нашли
        id_ = self.contour.find(point)
        if not id_:
            for hole in self.holes:
                id_ = hole.find(point)
        return id_  # двойной id или нет ?

    # добавление точки по сложному индексу
    def insert(self, id_: tuple, point: tuple = None):  # id_ = (id контура, ind точки)
        if point is None:
            point_x = (self[(id_[0], id_[1] - 1)][0] + self[id_][0])/2
            point_y = (self[(id_[0], id_[1] - 1)][1] + self[id_][1])/2
            point = (point_x, point_y)
        new_p_id = self.contour.insert(id_[1], point) if id_[0] == 0 else self.holes[id_[0] - 1].insert(id_[1], point)
        new_id = (id_[0], new_p_id)
        return new_id

    # верно в случае, если id и index совпадают
    def move(self, id_: tuple, new_coord: tuple):
        self.contour.move(id_[1], new_coord) if id_[0] == 0 else self.holes[id_[0] - 1].move(id_[1], new_coord)

    def move_all(self, vector: tuple):
        self.contour.move_all(vector)
        for hole in self.holes:
            hole.move_all(vector)

    def rotate(self, rotation_center: tuple, angle: float):
        self.contour.rotate(rotation_center, angle)
        for hole in self.holes:
            hole.rotate(rotation_center, angle)

    def pop(self, index: tuple):
        return self.contour.pop(index[1]) if index[0] == 0 else self.holes[index[0] - 1].pop(index[1])

    # проверить!
    def rem_id(self, id_: tuple):
        return self.contour.rem_id(id_[1]) if id_[0] == 0 else self.holes[id_[0] - 1].rem_id(id_[1])

    def segments(self):
        ans = copy(self.contour.segments())
        for hole in self.holes:
            ans.extend(hole.segments())
        return ans

    def points(self):  # массив массивов точек - более логично
        all_points = []
        all_points.append(self.contour.points())
        # list(map(lambda x: all_points.append(x), self.contour.points()))
        for hole in self.holes:
            all_points.append(hole.points())
            # list(map(lambda x: all_points.append(x), hole.points()))
        return all_points

    @property
    def raw(self):
        contour_ids = list(map(lambda x: (0, x), self.contour.raw))
        hole_ids_list = []
        for hole_id, hole in enumerate(self.holes):
            hole_ids = list(map(lambda x: (hole_id+1, x), hole.raw))
            hole_ids_list.append(hole_ids)
        return (contour_ids, hole_ids_list)

    def __str__(self):
        if not self.holes:
            holes = "-"
        else:
            holes = ", ".join(map(str, list(map(lambda x: x.points(), self.holes))))
        return "Polygon\nContour: " + str(self.contour.points()) + "\nHoles: " + holes + "\n"

    def __repr__(self):
        return self.__str__()

    # добавить разбиение на монотонные
    def add_bridges(self):
        # имеем координаты внешнего контура и контура дырок
        # добавить привидение к контуру с обходом против часовой
        # хотим получить координаты внешнего контура с мостиками, соединяющими его с дырами
        def cross_ray(edges, red_edge):
            point_of_cross = False
            crossing_edge = False
            n_hole = False
            # существует ли пересечение двух отрезков ed и y = geom_graph.get_point(face_list[face_id][0][1])[1]
            # левее, чем geom_graph.get_point(face_list[face_id][0][1])[0] = x - координате точки пересечения
            x_y = red_edge[1]  # конечная точка, из которой отправляем луч
            for level in range(len(edges)):
                for ed in edges[level]:
                    up, down = ed[0], ed[1]
                    if (down[1] - up[1] > eps) or ((abs(down[1] - up[1]) < eps) and (down[0] - up[0] > eps)):
                        continue  # если ребро идёт наверх или горизонтально слева направо, то мы его не рассматриваем
                    if (x_y[1] - up[1] > eps) or (down[1] - x_y[1] > eps) or ((x_y[0] - up[0] < eps) and (x_y[0] - down[0] < eps)):
                        continue  # точки пересечения точно нет
                    else:  # точка пересечения точно есть
                        if abs(up[1] - down[1]) < eps:
                            x_new = down[0]
                        else:
                            x_new = down[0] + ((x_y[1] - down[1]) * (up[0] - down[0])) / (up[1] - down[1])
                        if not point_of_cross:
                            point_of_cross, crossing_edge, n_hole = (x_new, x_y[1]), ed, level
                        elif x_new - point_of_cross[0] >= - eps:
                            point_of_cross, crossing_edge, n_hole = (x_new, x_y[1]), ed, level
            return point_of_cross, crossing_edge, n_hole  # вернуть точку и ребро и номер контура в записи полигона

        def next_edge(all_s, ed, ind):
            mod = len(all_s[ind])
            # тут нужно смотреть приблизительные значения, иначе вылетает
            ed_index = all_s[ind].index(ed)
            next_ed = all_s[ind][(ed_index + 1) % mod]
            return next_ed

        all_edges = []
        inner_contour_ccw = self.contour.segments(BypasDirection.CCW)
        all_edges.append(inner_contour_ccw)
        cw_holes = []
        bypas_direction = BypasDirection.CW
        list(map(lambda x: cw_holes.append(x.segments(bypas_direction)), self.holes))
        all_edges.extend(cw_holes)  # содержит все контуры по порядку, нулевой - внешний, далее контуры дырок
        h_left_edges = []
        for hole_contour in self.holes:
            h_left_edges.append(hole_contour.leftmost_edge(bypas_direction))
        value, key = [], []

        list(map(lambda x: value.append(cross_ray(all_edges, x)), h_left_edges))
        list(map(lambda x: key.append((x[0]+1, x[1])), enumerate(h_left_edges)))
        crossing_points_edges_holenums = {k: v for k, v in zip(key, value)}

        # геометрический граф оставим, для хранения точек
        for i, ed_coord in enumerate(h_left_edges):
            # nearest = list(crossing_points_edges_holenums.values())  # сделать словарь, где ключ - это значения key[0]
            nearest = {k[0]: v for k, v in zip(crossing_points_edges_holenums.keys(), crossing_points_edges_holenums.values())}
            # обработка правой части
            # индекс i относиться к нумерации дырок, в all edges этот индекс соответствует i+1
            next_ed_coord = next_edge(all_edges, ed_coord, i+1)  # poly_without_holes[1][i]
            # Рассмотрим левый контур, ищем: коорд. пересеч., ребро попадания коорд., по id, номер фэйса этого ребра
            # точка попадания, ребро попадания, номер контура в общем списке контуров
            left_center_point_coord, left_ed_coord, left_contour_num = nearest[i+1]  # индекс под вопросом
            # sub num - номер контура в all edges в который мы попали, выпустив луч
            next_left_ed_coord = next_edge(all_edges, left_ed_coord, left_contour_num)

            left_contour = []
            right_contour = []
            if left_center_point_coord == left_ed_coord[1]:  # так как можем попасть только в down
                # если попали в существующую вершину
                # тут нужны два соседних ребра
                # получаем новые точки, сдвигаясь от центральной по рёбрам на eps
                left_down_point, left_down_ed = cut_edge_on_epsilon(next_left_ed_coord, False)
                left_up_point, left_up_ed = cut_edge_on_epsilon(left_ed_coord, True)
                next_left_ed_coord = next_edge(all_edges, next_left_ed_coord, left_contour_num)
            else:
                # если попали на середину ребра, разбиваем его на два полуребра
                left_down_point, left_down_ed =\
                    cut_edge_on_epsilon((left_center_point_coord, left_ed_coord[1]), False)
                left_up_point, left_up_ed =\
                    cut_edge_on_epsilon((left_ed_coord[0], left_center_point_coord), True)

            while next_left_ed_coord != left_ed_coord:
                left_contour.append(next_left_ed_coord)
                next_left_ed_coord = next_edge(all_edges, next_left_ed_coord, left_contour_num)

            # теперь рассмотрим правый контур
            # в cut_edge_on_epsilon - True значит, что надо отрезать с конца вектора
            right_down_point, right_down_ed = cut_edge_on_epsilon(ed_coord, True)
            right_up_point, right_up_ed = cut_edge_on_epsilon(next_ed_coord, False)
            right_center_point = ed_coord[1]  # всегда вершина

            next_right_ed = next_edge(all_edges, next_ed_coord, i+1)
            while next_right_ed != ed_coord:
                right_contour.append(next_right_ed)
                next_right_ed = next_edge(all_edges, next_right_ed, i+1)

            # хотим отсортировать правые и левые точки по y, записываем в списки по id
            sorted_left = sortedcontainers.SortedKeyList(key=lambda point: point[1])
            sorted_left.add(left_down_point)
            sorted_left.add(left_center_point_coord)
            sorted_left.add(left_up_point)

            sorted_right = sortedcontainers.SortedKeyList(key=lambda point: point[1])
            sorted_right.add(right_down_point)
            sorted_right.add(right_center_point)
            sorted_right.add(right_up_point)

            # верхнее ребро моста - слева направо
            bridge_up_side = (sorted_left[2], sorted_right[2])
            # нижнее ребро моста - справа налево
            bridge_down_side = (sorted_right[0], sorted_left[0])

            up_line = (left_up_ed, bridge_up_side, right_up_ed)
            down_line = (right_down_ed, bridge_down_side, left_down_ed)
            temp_contour = [*right_contour, *down_line, *left_contour, *up_line]
            # получили цельный контур, хотим заменить на него прошлый левый контур и убрать обработанную дыру
            # переписать all edges и crossing_points_edges_holenums
            # ищем все рёбра из nearest_right_point: их left_ed совпадает с нашим
            new_crossing_points_edges_holenums = {}
            key_to_del = False
            for key, value in crossing_points_edges_holenums.items():
                if key[0] == i+1:
                    key_to_del = key
                    continue
                else:
                    if value[2] == i+1:  # если есть дыра, из которой мост приходит в рассматриваемую сейчас дыру
                        # надо поменять только номер контура, в который придет мост, так как старого номера уже не будет
                        crossing_points_edges_holenums[key] = (value[0], value[1], left_contour_num)
                    if value[2] == left_contour_num and value[1] == left_ed_coord:
                        # если попали мостом в контур, в который уже попадал мост
                        # надо менять ребро попадания, если попали
                        new_crossing_points_edges_holenums[key] = value
            if key_to_del:  # чтобы не рассматривать уже рассмотренные контура
                crossing_points_edges_holenums.pop(key_to_del)
            # меняем nearest_right_point от нужных ключей
            for key, edge_and_point in new_crossing_points_edges_holenums.items():

                if edge_and_point[0][1] < left_center_point_coord[1]:
                    crossing_points_edges_holenums[key] = (edge_and_point[0], left_down_ed, edge_and_point[2])
                else:
                    crossing_points_edges_holenums[key] = (edge_and_point[0], left_up_ed, edge_and_point[2])
            all_edges[left_contour_num] = temp_contour
            all_edges[i+1] = []  # оставляем пустой - ?
        # перевод в точки
        new_contour = []
        list(map(lambda x: new_contour.append(x[0]), all_edges[0]))
        cutting_poly = Polygon(new_contour, [])  # возвращаем полигон
        return cutting_poly


""" 
cont = [(10, 2), (2, 2), (2, 9), (10, 9)]
holes = [[(6, 6), (4, 6), (4, 8), (6, 8)], [(5, 3), (3, 3), (3, 5), (5, 5)], [(9, 3), (7, 3), (7, 5), (9, 5)]]
pol1 = Polygon(cont, holes)

poly = [(1, 1), (12, -2), (16, 2), (12, 12), (1, 13), (2, 9), (0, 5), (16, 2)]
pline = PLine(poly)

group = Group([pol1, pline])
ans1 = group.segments()
ans2 = group.points()
ans3 = group.raw
group.move_all((1, 1))
b = 0

 
poly = [(1, 1), (12, -2), (16, 2), (12, 12), (1, 13), (2, 9), (0, 5), (16, 2)]
a = PointChain(poly)
a.rem_all_p((16, 2))
v = a.self_intersect()
# pop insert move
a.pop(2)
a.insert(2, (1, 1))
a.move(1, (5, 8))  # по индексу
b = 2

cont = [(10, 2), (2, 2), (2, 9), (10, 9)]
holes = [[(6, 6), (4, 6), (4, 8), (6, 8)], [(5, 3), (3, 3), (3, 5), (5, 5)], [(9, 3), (7, 3), (7, 5), (9, 5)]]
pol1 = Polygon(cont, holes)
cnt = pol1.get_all_contours()
c_p = pol1.add_bridges()
a = c_p.get_segments()  # всё ок!!!
gg = pol1.insert((0, 1), (9, 3))  # id
pol1.move((2, 0), (6, 3))  # -
ki = pol1[(1, 3)]  # point
dd = pol1.pop((3, 2))  # id
b = 2

"""
