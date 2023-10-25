from enum import Enum
import math
import sys
import matplotlib.pyplot as plt
import random
from sortedcontainers import SortedList, SortedKeyList

eps = 0.0000001
delta = 0.02


def edge_generator(count):  # count of edges
    init_points = []
    init_edges = []
    x_size = 1000
    y_size = 1000
    for point_number in range(count * 2):
        rand_x = round(random.random() * x_size, 2)
        rand_y = round(random.random() * y_size, 2)
        init_points.append((rand_x, rand_y))
        if point_number % 2 == 1:
            init_edges.append([init_points[point_number - 1], init_points[point_number]])
    return init_points, init_edges


# рисуем график
def draw_graph(segments_list, cross_points, a=None, b=None, c=None, d=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')

    for ed in segments_list:
        if isinstance(ed, Edge):
            show_list_x = [ed.beg_x, ed.end_x]
            show_list_y = [ed.beg_y, ed.end_y]
        else:
            show_list_x = [ed[0][0], ed[1][0]]
            show_list_y = [ed[0][1], ed[1][1]]
        rnd_r = random.random()
        rnd_g = random.random()
        rnd_b = random.random()
        plt.plot(show_list_x, show_list_y, marker='o', color=(rnd_r, rnd_g, rnd_b))
    for pnt in cross_points:
        p_x = pnt[0]
        p_y = pnt[1]
        plt.plot(p_x, p_y, 'ko')
    if a is not None:
        ax.set_xlim(a, b)
        ax.set_ylim(c, d)
    plt.show()


class PointLoc(Enum):
    LEFT = 1
    RIGHT = 2
    BEYOND = 3
    BEHIND = 4
    BETWEEN = 5
    ORIGIN = 6
    DESTINATION = 7


class Intersect(Enum):
    COLLINEAR = 1
    PARALLEL = 2
    SKEW = 3
    SKEW_CROSS = 4
    SKEW_NO_CROSS = 5


def dot_product(p, q):
    return p[0] * q[0] + p[1] * q[1]


class Edge(object):
    __slots__ = 'edge', 'info'

    def __init__(self, ed, inf=None):
        self.edge = ed
        self.info = inf

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str(self.edge) if self.info is None else str(self.edge) + ', ' + str(self.info)

    def __getitem__(self, item):
        return self.edge[item]

    @property
    def get_info(self):
        return self.info

    @property
    def get_edge(self):
        return self.edge

    @property
    def beg(self):
        return self.edge[0]

    @property
    def beg_x(self):
        return self.beg[0]

    @property
    def beg_y(self):
        return self.beg[1]

    @property
    def end(self):
        return self.edge[1]

    @property
    def end_x(self):
        return self.end[0]

    @property
    def end_y(self):
        return self.end[1]

    @property
    def export_to_list(self):
        return [(self.beg_x, self.beg_y), (self.end_x, self.end_y)]

    def __eq__(self, other):  # сравниваем только саму точку
        return self.edge == other.edge

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self.edge < other.edge

    def __gt__(self, other):
        return self.edge > other.edge

    def __round__(self, n=5):
        return Edge(self.round_val(self.edge, n))

    @staticmethod  # переделать!
    def round_val(ed, n=5):
        f1 = round(ed[0][0], n)
        f2 = round(ed[0][1], n)
        f3 = round(ed[1][0], n)
        f4 = round(ed[1][1], n)
        return [(f1, f2), (f3, f4)]

    def turn_right(self, epsilon=eps):
        if self.beg_x - self.end_x > epsilon:
            self.edge = [self.end, self.beg]
        if abs(self.beg_x - self.end_x) < epsilon and (self.beg_y - self.end_y > epsilon):
            self.edge = [self.end, self.beg]

    def tg(self):
        """ Returns the tangent of the angle between the edge and the positive x-axis direction. """
        return (self.beg_y - self.end_y) / (self.beg_x - self.end_x + eps)

    def find_relative_position(self, point, epsilon=eps):
        """
        Classification of the position of the point relative to the segment with
        the beginning at the point other1 and the end at the point other2.
        """
        ax = self.end_x - self.beg_x
        ay = self.end_y - self.beg_y
        bx = point[0] - self.beg_x
        by = point[1] - self.beg_y
        sa = ax * by - bx * ay
        if sa > epsilon:
            return PointLoc.LEFT
        if sa < - epsilon:
            return PointLoc.RIGHT
        if abs(self.beg_x - point[0]) < epsilon and abs(self.beg_y - point[1]) < epsilon:
            return PointLoc.ORIGIN
        if abs(self.end_x - point[0]) < epsilon and abs(self.end_y - point[1]) < epsilon:
            return PointLoc.DESTINATION
        if (ax * bx < 0.0) or (ay * by < 0.0):
            return PointLoc.BEHIND
        if math.sqrt(ax * ax + ay * ay) < math.sqrt(bx * bx + by * by):
            return PointLoc.BEYOND
        return PointLoc.BETWEEN

    def is_intersect(self, other):  # скрещивающиеся или параллельные
        """
        Epsilon classification of the position of lines containing segments other and edge.
        Options: parallel, collinear, skew (скрещивающиеся).
        """
        a = other.beg
        b = other.end
        c = self.beg
        d = self.end
        n = ((d[1] - c[1]), (c[0] - d[0]))

        denom = dot_product(n, (b[0] - a[0], b[1] - a[1]))  # b - a
        if denom == 0.0:
            aclass = other.find_relative_position(a)
            if (aclass == PointLoc.LEFT) or (aclass == PointLoc.RIGHT):
                return Intersect.PARALLEL, float('inf')
            else:
                return Intersect.COLLINEAR, float('inf')
        num = dot_product(n, (a[0] - c[0], a[1] - c[1]))  # a - c
        t = - num / denom
        return Intersect.SKEW, t

    def is_cross(self, other):  # пересекаются ли сами отрезки или их продолжения
        """
        Epsilon classification of the position of two segments relative to each other.
        Options: skew and intersecting within segments,
                 skew and non-intersecting within segments.
        """
        cross_type, s = self.is_intersect(other)
        if (cross_type == Intersect.COLLINEAR) or (cross_type == Intersect.PARALLEL):
            return cross_type, s
        if (s < - eps) or (s > 1.0 + eps):
            return Intersect.SKEW_NO_CROSS, s
        cross_type, t = other.is_intersect(self)
        if (t >= 0.0 - eps) and (t <= 1.0 + eps):
            return Intersect.SKEW_CROSS, t
        else:
            return Intersect.SKEW_NO_CROSS, t

    def is_vertical(self):
        return abs(self.end_x - self.beg_x) < eps

    def is_horizontal(self):
        return abs(self.end_y - self.beg_y) < eps

    def get_parametric_pos_of(self, point: tuple):
        if self.find_relative_position(point) in [PointLoc.BETWEEN, PointLoc.ORIGIN, PointLoc.DESTINATION]:
            return (point[1] - self.beg_y) / (self.end_y - self.beg_y) if self.is_vertical() else (point[0] - self.beg_x) / (self.end_x - self.beg_x)
        else:
            return None

    def get_point_by_parameter(self, t):
        """ Return the point:tuple of the edge, corresponding to the parameter t. """
        #      edge[0][0] + (edge[1][0] - edge[0][0]) * t, edge[0][1] + (edge[1][1] - edge[0][1]) * t
        return self.beg_x + (self.end_x - self.beg_x) * t, self.beg_y + (self.end_y - self.beg_y) * t

    def get_y_coordinate_by(self, x):
        if abs(self.beg_x - self.end_x) < eps:
            return self.beg_y
        return self.beg_y + (self.end_y - self.beg_y) * (x - self.beg_x) / (self.end_x - self.beg_x)

    def get_sorted_list_for_status(self, other):  # for edges with same beg_y
        if self.end_x <= other.end_x:   # возможно просто <
            return [other, self] if self.end_y > other.get_y_coordinate_by(self.end_x) else [self, other]
        else:
            return [self, other] if other.end_y > self.get_y_coordinate_by(other.end_x) else [other, self]


class StatusList(object):
    __slots__ = 'new_list'

    def __init__(self, old_list=None):
        if old_list:
            self.new_list = old_list
            self.new_list.sotr()
        else:
            self.new_list = []

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        ans = ""
        for n_e in self.new_list:
            ans += str(n_e) + '\n'
        return ans

    # сделать static метод
    def update_y(self, new_edge: Edge):
        """
        Returns a new edge sequence including the new_edge.
        The order of the edges corresponds to the order of the Status.
        """
        edges = self.new_list
        new_x, new_y = new_edge.beg_x, new_edge.beg_y

        if len(edges) == 1:  # если в списке только одно ребро, добавляем второе
            edge = edges[0]
            curr_y = edge.get_y_coordinate_by(new_x)
            if new_y == curr_y:  # если начала по y совпадают, добавить eps - ?
                return edge.get_sorted_list_for_status(new_edge)
            return [edge, new_edge] if new_y > curr_y else [new_edge, edge]

        # бинпоиск по позиции отрезка в статусе, искомая позиция находится между существующими
        modified_edges = [((-sys.maxsize, -sys.maxsize), (sys.maxsize, -sys.maxsize))]
        modified_edges.extend(edges)
        modified_edges.append(((-sys.maxsize, sys.maxsize), (sys.maxsize, sys.maxsize)))
        low = 0
        high = len(modified_edges) - 1
        while low <= high:
            mid = low + (high - low) // 2
            guess = modified_edges[mid]
            guess_y = guess.get_y_coordinate_by(new_x)

            if abs(guess_y - new_y) < eps:
                if guess.get_sorted_list_for_status(new_edge)[0] == guess:
                    low = mid
                else:
                    high = mid
                # сортируем отрезки по углу наклона, проверить внимательно на тестовых данных!
                # возможно удалить эту часть
                if guess.end_x <= new_edge.end_x:  # ищем минимальную x координату концов рёбер
                    if guess.end_y > new_edge.get_y_coordinate_by(guess.end_x):
                        high = mid
                        # сравниваем значение y в этой точке
                    else:
                        low = mid
                else:
                    if new_edge.end_y > guess.get_y_coordinate_by(new_edge.end_x):  # сравниваем значение y в этой точке
                        low = mid
                    else:
                        high = mid
            elif guess_y < new_y:
                low = mid
            else:
                high = mid

            if high - low == 1:
                break
        y_pos = low
        edges.insert(y_pos, new_edge)
        return edges

    def add(self, new_edge):
        if not self.new_list:
            self.new_list.append(new_edge)
        else:
            self.new_list = self.update_y(new_edge)  # возможно ничего не возвращать?!

    def cross_edges(self, pos1, pos2):  # надо поменять позиции двух соседних пересекающееся рёбер в статусе
        self.new_list[pos1], self.new_list[pos2] = self.new_list[pos2], self.new_list[pos1]

    def delete_edge(self, edge):
        self.new_list.remove(edge)

    def swap_edges(self, lri_edge):
        index_in_status = []
        last_part = lri_edge.get_last_parts_i_p()
        for i in lri_edge.i_p:  # проверить, как работает, если несколько рёбер!
            # last_part.append([lri_edge.p, i[1]])
            try:
                index_in_status.append(self.index(i))
            except ValueError:
                print(self.new_list)
        for index in index_in_status:
            self.new_list[index] = last_part.pop()

    def cut_left_part(self, ind, edge):
        self.new_list[ind] = edge

    def index(self, current_edge):

        return self.new_list.index(current_edge)

    def __getitem__(self, item):
        return self.new_list[item]

    def len(self):
        return len(self.new_list)


# сделать if
def match(edge_list, another_edge):  # добавляем ребро в список рёбер, если его там ещё нет
    try:
        edge_list.index(another_edge)
    except ValueError:  # если пришло новое ребро
        edge_list.add(another_edge)


def match_2(edge_list, another_edge):
    tg_list = SortedKeyList(map(lambda x: x.tg(), edge_list))
    another_tg = (another_edge.beg_y - another_edge.end_y) / (
                another_edge.beg_x - another_edge.end_x + eps)
    if len(tg_list):
        add_edge_flag = False
        edge_remove_list = []
        for i in range(len(tg_list)):
            if abs(tg_list[i] - another_tg) < delta:
                if abs(edge_list[i].beg_x - another_edge.beg_x) > eps and abs(
                        edge_list[i].beg_y - another_edge.beg_y) > eps:
                    if another_edge.beg_x > edge_list[i].beg_x:
                        edge_remove_list.append(edge_list[i])
                        add_edge_flag = True
            else:
                add_edge_flag = True
        # удаляем после прохождения по всему массиву, чтобы не возникала ошибка выхождения за границу
        for edge in edge_remove_list:
            edge_list.remove(edge)
    else:
        add_edge_flag = True
    if add_edge_flag:
        edge_list.add(another_edge)


# возможно не нужно - ?
def approximate_match(edge_list, another_edge: Edge):
    # добавляем ребро в список рёбер, если его там ещё нет, с учётом возможности неточных значений на концах
    # теперь это объекты класса Edge, раньше были списками списков
    ap_v1 = SortedKeyList(map(lambda x: round(x), edge_list))  # проверить !!
    ap_v2 = round(another_edge)
    try:
        # проверить работает ли, учитывая, что теперь ищем сложный класс
        ap_v1.index(ap_v2)  # как найти приблизительно
    except ValueError:  # если пришло новое ребро
        edge_list.add(another_edge)


def approximate_match_2(edge_list, another_edge: Edge):
    ap_v1_end = list(map(lambda x: x.__round__().end, edge_list))
    ap_v2_end = another_edge.__round__().end

    ap_v1_beg = list(map(lambda x: x.__round__().beg, edge_list))
    ap_v2_beg = another_edge.__round__().beg
    try:
        index = ap_v1_end.index(ap_v2_end)  # нашли отрезок с тем же концом
        # дальше 2 варианта, это отрезок полностью повторяется, или начало разное
        if isinstance(ap_v1_beg[index], tuple) or isinstance(ap_v2_beg.beg, tuple):
            aaa = 111
        if ap_v1_beg[index] < ap_v2_beg:
            edge_list.remove(edge_list[index])
            edge_list.add(another_edge)

    except ValueError:  # если пришло новое ребро
        edge_list.add(another_edge)


class LRI(object):
    __slots__ = ('p', 'r_p', 'l_p', 'i_p')

    def __init__(self, p, edges, cross=False):
        self.p = p
        self.r_p = SortedKeyList()
        self.l_p = SortedKeyList()
        self.i_p = SortedKeyList(key=Edge.__round__)

        for ed in edges:
            if isinstance(ed, Edge):
                edge = ed
            else:
                edge = Edge(ed)
            # если ребро идёт не слева на право, то поменять конечные точки местами
            edge.turn_right()
            p_type = edge.find_relative_position(p)
            if p_type == PointLoc.ORIGIN:
                self.l_p.add(edge)
            elif p_type == PointLoc.DESTINATION:
                self.r_p.add(edge)
            elif p_type in (PointLoc.BETWEEN, PointLoc.LEFT, PointLoc.RIGHT):
                if cross:
                    # добавить проверку точки на близость
                    self.i_p.add(edge)

    def get_last_parts_i_p(self):
        l_p = []
        for i in self.i_p:  # проверить, как работает, если несколько рёбер!
            l_p.append(Edge([self.p, i.end], i.info))
        return l_p

    def adding(self, other):  # функция добавления новых рёбер к существующей точке
        list(map(lambda x: approximate_match_2(self.i_p, x), other.i_p))  # новые рёбра добавляются поочерёдно
        list(map(lambda x: match_2(self.r_p, x), other.r_p))
        list(map(lambda x: match(self.l_p, x), other.l_p))

    def __eq__(self, other):  # сравниваем только саму точку
        return (abs(self.p[0] - other.p[0]) < eps) and (abs(self.p[1] - other.p[1]) < eps)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return (self.p[0] - other.p[0]) < -eps or (
                abs(self.p[0] - other.p[0]) < eps and (self.p[1] - other.p[1]) < - eps)

    def __gt__(self, other):
        return (self.p[0] - other.p[0]) > eps or (abs(self.p[0] - other.p[0]) < eps < (self.p[1] - other.p[1]))

    def __repr__(self):
        s = "Point {}: l_p={}, i_p={}, r_p={}\n".format(self.p, list(self.l_p), list(self.i_p), list(self.r_p))
        return s


# переделать эту функцию!!
def point_check(point_ind, s_l_of_edges, i_p_del, r_p_del, l_p_del):
    # проверка точки на совпадение с той, которую хотим удалить, проверяем не координату, а содержимое
    flag = - 1
    i_p_need_to_be_deleted = []
    r_p_need_to_be_deleted = []
    l_p_need_to_be_deleted = []

    while i_p_del:
        test_edges = s_l_of_edges[point_ind].i_p
        if test_edges:
            for ed in test_edges:
                # если концы отрезков совпадают
                if ed.end == i_p_del[0].end:
                    flag += 1
                    i_p_need_to_be_deleted.append(ed)
                    break
            # pop тут, тк мб вариант (i_p_del и test_edges) != 0 и не имеют пересечений
            i_p_del.pop(0)
        else:
            break
            # сразу удалить этот отрезок ed из LRI_sorted_list[element].i_p

    # хотим проверить r_p, их вторая координата всегда равна нашей точке, поэтому
    # проверяем принадлежность точки отрезку

    while r_p_del:
        test_edges = s_l_of_edges[point_ind].r_p
        if test_edges:
            for ed in test_edges:
                test_class = ed.find_relative_position(r_p_del[0].beg, epsilon=0)
                if test_class in (PointLoc.ORIGIN, PointLoc.BETWEEN):
                    flag += 1
                    r_p_need_to_be_deleted.append(ed)
                    break
            r_p_del.pop(0)
        else:
            break
    while l_p_del:
        test_edges = s_l_of_edges[point_ind].l_p
        if test_edges:
            for ed in test_edges:
                test_class = ed.find_relative_position(l_p_del[1].beg)
                if test_class in (PointLoc.BETWEEN, PointLoc.DESTINATION):
                    flag += 1
                    l_p_need_to_be_deleted.append(ed)
                    break
            l_p_del.pop(0)
        else:
            break
    if flag == 1:  # если совпали оба пересекающихся в данной точке отрезка
        for el in i_p_need_to_be_deleted:
            s_l_of_edges[point_ind].i_p.remove(el)
        for el in r_p_need_to_be_deleted:
            s_l_of_edges[point_ind].r_p.remove(el)
        for el in l_p_need_to_be_deleted:
            s_l_of_edges[point_ind].l_p.remove(el)

        return point_ind
    else:
        return -1


def bentli_ottman(edge_list, get_additional_info=False):
    if len(edge_list) == 1:
        answer = edge_list
        return answer
    point_list = set()
    for edge in edge_list:
        point_list.add(edge[0])
        point_list.add(edge[1])
    # добавить проверку на близость точек
    LRI_list = []
    for point in point_list:
        new_p = LRI(point, edge_list, False)
        LRI_list.append(new_p)

    LRI_sorted_list = SortedList(LRI_list)

    status = StatusList()
    answer = []
    # найденные точки пересечения
    intersection_points = []
    if get_additional_info:
        some_data = SortedKeyList(key=lambda str: str[0])
    circle = 0
    current_point = LRI_sorted_list[2]

    def get_new_point(ind1, ind2, param_t):
        new_coord_x, new_coord_y = status[ind1].get_point_by_parameter(param_t)
        n_p = (new_coord_x, new_coord_y)
        n_e_list = [status[ind1], status[ind2]]  # всего два ребра
        return LRI(n_p, n_e_list, True)

    # основной алгоритм
    while len(LRI_sorted_list) > 0:
        new_current_point = LRI_sorted_list.pop(0)
        # костыль на случай если во время обработки точки в список точек добавится та же точка ещё раз,
        # никакой новой инфы она не принесёт, надо исправить в дальнейшем
        # сравниваем точку из предыдущей итерации и новую точку
        if circle > 0 and current_point == new_current_point:
            continue
        circle += 1
        # для проверки на наличие одинаковых точек
        # сравниваем новую точку и точку которая идёт за ней в цикле
        multi_point = new_current_point
        while LRI_sorted_list and LRI_sorted_list[0] == new_current_point:  # осуществляем приблизительное сравнение
            current_point = LRI_sorted_list.pop(0)
            multi_point.adding(current_point)
        current_point = multi_point

        if current_point.r_p:
            # найдём отрезки заканчивающиеся на current_point в status
            ends_of_edges = []
            # нужен бинпоиск
            for edge_index in range(status.len()):
                if LRI(status[edge_index].end, []) == current_point:
                    ends_of_edges.append(status[edge_index])
                    if edge_index < status.len() - 1:
                        intersection, t = status[edge_index].is_cross(status[edge_index + 1])
                        if intersection == Intersect.SKEW_CROSS and 0 < t <= 1:
                            # add_in_lri(edge_index, edge_index + 1, t)
                            new_p = get_new_point(edge_index, edge_index + 1, t)
                            if new_p == new_current_point:  # необходимо приблизительное сравнение
                                current_point.adding(new_p)
                            else:
                                LRI_sorted_list.add(new_p)

                    if 0 < edge_index < status.len() - 1:
                        intersection, t = status[edge_index - 1].is_cross(status[edge_index + 1])
                        if intersection == Intersect.SKEW_CROSS and 0 < t < 1:
                            new_p = get_new_point(edge_index - 1, edge_index + 1, t)
                            if new_p == new_current_point:  # необходимо приблизительное сравнение
                                current_point.adding(new_p)
                            else:
                                LRI_sorted_list.add(new_p)

            list(map(lambda x: status.delete_edge(x), ends_of_edges))  # исключить отрезки из статуса
            list(map(lambda x: answer.append(x), ends_of_edges))

        # приводим статус к состоянию соответствующему положению сканирующей прямой после прохождения current_point
        if current_point.i_p:
            intersection_points.append(current_point.p)  # нужно ли тут - ?
            if get_additional_info:
                inf_list = list(current_point.l_p)
                inf_list.extend(list(current_point.i_p))
                inf_list.extend(list(current_point.r_p))
                some_data.add([current_point.p, inf_list])
            status.swap_edges(current_point)  # меняем местами отрезки в статусе, оставляя только правые части
        if current_point.l_p:
            list(map(lambda x: status.add(x), current_point.l_p))

        # осуществляем поиск новых точек пересечения
        if current_point.l_p:  # если точка - начало отрезка
            # добавили все отрезки исходящие из этой точки
            # список индексов в статусе отрезков добавленных на прошлом шаге
            index_list = list(map(lambda x: status.index(x), current_point.l_p))
            # сортировка индексов
            index_list.sort()
            if status.len() > 1:  # проверка на необходимость поиска точек пересечения
                for index in index_list:  # проходимся по отрезкам в статусе (те, что только добавили)
                    if index == 0:  # отдельно для первого отрезка
                        intersection, t = status[0].is_cross(status[1])
                        if intersection == Intersect.SKEW_CROSS and 0 < t < 1:
                            new_p = get_new_point(0, 1, t)
                            LRI_sorted_list.add(new_p)

                    elif index == status.len() - 1:  # для последнего отрезка
                        intersection, t = status[index].is_cross(status[status.len() - 2])
                        if intersection == Intersect.SKEW_CROSS and 0 <= t < 1:
                            if abs(t) < eps:  # случай начала в одной точке вертикальной и другой линии
                                if status[status.len() - 2].beg != current_point.p:  # переделать !
                                    answer.append([status[status.len() - 2].beg, current_point.p])
                                status.cut_left_part(status.len() - 2, Edge([current_point.p, status[status.len() - 2].end], status[status.len() - 2].info ))
                                # list(map(lambda x: answer.append(x), left_part))  # добавляем отрезки в ответ

                                if status.len() > 2:
                                    intersection, t = status[status.len() - 2].is_cross(status[status.len() - 3])
                                    if intersection == Intersect.SKEW_CROSS and 0 <= t < 1:
                                        new_p = get_new_point(status.len() - 2, status.len() - 3, t)
                                        LRI_sorted_list.add(new_p)

                            else:
                                new_p = get_new_point(status.len() - 1, status.len() - 2, t)
                                LRI_sorted_list.add(new_p)

                    else:  # отрезок не крайний
                        intersection, t = status[index - 1].is_cross(status[index + 1])
                        # если пересекаются соседи с обеих сторон, нужно удалить точку их пересечения по алгоритму БО
                        # возможно 0 < t < 1 + eps
                        if intersection == Intersect.SKEW_CROSS and 0 < t < 1:
                            new_p = get_new_point(index - 1, index + 1, t)
                            # чтобы удалить точку события их пересечения, надо её найти в LRI_sorted_list
                            # проверим следующую точку в LRI с индексом = 0
                            checked_ind = point_check(0, LRI_sorted_list, new_p.i_p, new_p.r_p,
                                                      new_p.l_p)
                            if LRI_sorted_list[0] == new_p and checked_ind > -1:
                                LRI_sorted_list.pop(0)
                            else:
                                # если она не первая, то ищем её бинпоиском
                                low = 0
                                high = len(LRI_sorted_list) - 1
                                while low <= high:
                                    mid = low + (high - low) // 2
                                    guess = LRI_sorted_list[mid]

                                    if guess == new_p:
                                        checked_ind = point_check(mid, LRI_sorted_list, new_p.i_p, new_p.r_p, new_p.l_p)
                                        if checked_ind > -1:
                                            LRI_sorted_list.pop(mid)
                                        break
                                    elif guess < new_p:
                                        low = mid
                                    else:
                                        high = mid

                                    if high - low == 1:  # при рассмотрении точки из которой выходят несколько отрезков
                                        break
                        intersection, t = status[index].is_cross(status[index + 1])
                        if intersection == Intersect.SKEW_CROSS and 0 < t < 1 + eps:  # если пересекается с верхним соседом
                            new_p = get_new_point(index, index + 1, t)
                            LRI_sorted_list.add(new_p)

                        intersection, t = status[index].is_cross(status[index - 1])
                        if intersection == Intersect.SKEW_CROSS and 0 <= t < 1:  # если пересекается с нижним соседом
                            if abs(t) < eps:
                                # рассматриваем только нижний отрезок, верхний уже рассмотрели
                                if status[index - 1].beg != current_point.p:
                                    left_part = [status[index - 1].beg, current_point.p]
                                    answer.append(left_part)
                                status.cut_left_part(index - 1, Edge([current_point.p, status[index - 1].end], status[index - 1].info))

                                if status.len() > 2:
                                    # проверяем оба соседа и пересечение вокруг - ?
                                    intersection, t = status[index + 1].is_cross(status[index - 1])
                                    if intersection == Intersect.SKEW_CROSS and 0 <= t < 1 + eps:
                                        new_point_x, new_point_y = status[index - 1].get_point_by_parameter(t)
                                        new_point = (new_point_x, new_point_y)
                                        new_p = LRI(new_point, [], False)
                                        # удалить надо только, если у точки есть сразу оба! для этого используем flag
                                        i_p_del, r_p_del, l_p_del = [], [], []

                                        cur_edges_for_delete = [status[index - 1], status[index + 1]]
                                        # удаление точки, как в r_p
                                        # возможно добавить сравнение с точностью eps
                                        for i in range(2):
                                            loc = cur_edges_for_delete[i].find_relative_position(new_point)
                                            if loc == PointLoc.BETWEEN:
                                                i_p_del.append(cur_edges_for_delete[i])
                                            elif loc == PointLoc.ORIGIN:
                                                l_p_del.append(cur_edges_for_delete[i])
                                            elif loc == PointLoc.DESTINATION:
                                                r_p_del.append(cur_edges_for_delete[i])

                                        # НАДО ПРАВИЛЬНО ВЫБРАТЬ КАКУЮ ТОЧКУ УДАЛЯТЬ
                                        # найти совпадение значения точки и совпадение концов отрезков
                                        # которых она содержит
                                        indexes_of_deleted_elements = []
                                        low = 0
                                        high = len(LRI_sorted_list) - 1
                                        while low <= high:
                                            mid = low + (high - low) // 2
                                            guess = LRI_sorted_list[mid]
                                            # проверка на совпадение x и y координат с точностью до eps;
                                            if guess == new_p:
                                                # рассматриваем конкретную точку
                                                # в LRI может быть несколько одинаковых точек,
                                                # но с разными отрезками в комплекте,
                                                # надо удалить только те точки, которые содержат нужные отрезки
                                                # сперва проверим срединные отрезки
                                                checked_ind = point_check(mid, LRI_sorted_list, i_p_del, r_p_del,
                                                                          l_p_del)
                                                if checked_ind > -1:
                                                    indexes_of_deleted_elements.append(checked_ind)
                                                # могут быть и соседние точки
                                                forward = 1
                                                while (mid + forward) < len(LRI_sorted_list) and LRI_sorted_list[
                                                    mid + forward] == new_p:
                                                    checked_ind = point_check(mid + forward, LRI_sorted_list, i_p_del,
                                                                              r_p_del, l_p_del)
                                                    if checked_ind > -1:
                                                        indexes_of_deleted_elements.append(checked_ind)
                                                    forward += 1
                                                revers = 1
                                                while (mid - revers) > 0 and LRI_sorted_list[mid - revers] == new_p:
                                                    checked_ind = point_check(mid - revers, LRI_sorted_list, i_p_del,
                                                                              r_p_del, l_p_del)
                                                    if checked_ind > -1:
                                                        indexes_of_deleted_elements.append(checked_ind)
                                                    revers += 1
                                                break

                                            elif guess < new_p:
                                                low = mid
                                            else:
                                                high = mid
                                            # тут мы нашли нужную точку, остальные могут быть только за или перед ней
                                            if high - low == 1:
                                                break

                                        # тут нужно удалить верную точку из LRI,
                                        # если эта точка ничего больше не содержит, то есть пустая
                                        for del_ind in indexes_of_deleted_elements:
                                            if not LRI_sorted_list[del_ind].r_p and not LRI_sorted_list[
                                                del_ind].i_p and not \
                                                    LRI_sorted_list[del_ind].l_p:
                                                LRI_sorted_list.pop(del_ind)
                            else:
                                new_p = get_new_point(index, index - 1, t)
                                LRI_sorted_list.add(new_p)

        if current_point.i_p:  # если точка - середина отрезка
            left_part = []
            right_part = []
            for i in current_point.i_p:
                right_part.append(Edge([current_point.p, i.end], i.info))
                if i.beg != current_point.p:
                    left_part.append(Edge([i.beg, current_point.p], i.info))
            if left_part:
                list(map(lambda x: answer.append(x), left_part))  # добавляем отрезки в ответ
                """
            if not current_point.l_p and not current_point.r_p:
                intersection_points.append(current_point.p)
                """
            #  теперь точка пересечения - это левая точка для двух новых отрезков, и их тоже надо обработать
            index_list = list(map(lambda x: status.index(x), right_part))
            index_list.sort()  # список индексов в статусе отрезков добавленных на прошлом шаге
            if status.len() > 1:  # проверка на необходимость поиска точек пересечения
                for index in index_list:  # проходимся по отрезкам в статусе
                    if index == 0:  # отдельно для первого отрезка
                        intersection, t = status[0].is_cross(status[1])

                        if intersection == Intersect.SKEW_CROSS and 0 < t < 1:
                            new_p = get_new_point(0, 1, t)
                            LRI_sorted_list.add(new_p)

                    elif index == status.len() - 1:  # для последнего отрезка
                        intersection, t = status[status.len() - 1].is_cross(status[status.len() - 2])
                        if intersection == Intersect.SKEW_CROSS and 0 < t < 1:
                            new_p = get_new_point(status.len() - 1, status.len() - 2, t)
                            LRI_sorted_list.add(new_p)

                    else:  # остальные случаи
                        intersection, t = status[index - 1].is_cross(status[index + 1])
                        if intersection == Intersect.SKEW_CROSS and 0 < t < 1 + eps:

                            new_point_x, new_point_y = status[index - 1].get_point_by_parameter(t)
                            new_point = (new_point_x, new_point_y)
                            new_p = LRI(new_point, [], False)
                            # удалить надо только, если у точки есть сразу оба! для этого используем flag
                            i_p_del = []
                            r_p_del = []
                            l_p_del = []
                            cur_edges_for_delete = [status[index - 1], status[index + 1]]

                            for i in range(2):
                                loc = cur_edges_for_delete[i].find_relative_position(new_point)
                                if loc == PointLoc.BETWEEN:
                                    i_p_del.append(cur_edges_for_delete[i])
                                elif loc == PointLoc.ORIGIN:
                                    l_p_del.append(cur_edges_for_delete[i])
                                elif loc == PointLoc.DESTINATION:
                                    r_p_del.append(cur_edges_for_delete[i])

                            # НАДО ПРАВИЛЬНО ВЫБРАТЬ КАКУЮ ТОЧКУ УДАЛЯТЬ
                            # найти совпадение значения точки и совпадение концов отрезков, которых она содержит

                            indexes_of_deleted_elements = []
                            low = 0
                            high = len(LRI_sorted_list) - 1
                            while low <= high:
                                mid = low + (high - low) // 2
                                guess = LRI_sorted_list[mid]
                                # проверка на совпадение x и y координат с точностью до eps;
                                if guess == new_p:
                                    # рассматриваем конкретную точку
                                    # в LRI может быть несколько одинаковых точек, но с разными отрезками в комплекте,
                                    # надо удалить только те точки, которые содержат нужные отрезки
                                    # сперва проверим срединные отрезки
                                    checked_ind = point_check(mid, LRI_sorted_list, i_p_del, r_p_del, l_p_del)
                                    if checked_ind > -1:
                                        indexes_of_deleted_elements.append(checked_ind)
                                    # могут быть и соседние точки
                                    forward = 1
                                    while (mid + forward) < len(LRI_sorted_list) and LRI_sorted_list[
                                        mid + forward] == new_p:
                                        checked_ind = point_check(mid + forward, LRI_sorted_list, i_p_del, r_p_del,
                                                                  l_p_del)
                                        if checked_ind > -1:
                                            indexes_of_deleted_elements.append(checked_ind)
                                        forward += 1
                                    revers = 1
                                    while (mid - revers) > 0 and LRI_sorted_list[mid - revers] == new_p:
                                        checked_ind = point_check(mid - revers, LRI_sorted_list, i_p_del, r_p_del,
                                                                  l_p_del)
                                        if checked_ind > -1:
                                            indexes_of_deleted_elements.append(checked_ind)
                                        revers += 1
                                    break

                                elif guess < new_p:
                                    low = mid
                                else:
                                    high = mid
                                # тут мы нашли нужную точку, остальные могут быть только за или перед ней
                                if high - low == 1:
                                    break
                            # тут нужно удалить верную точку из LRI,
                            # если эта точка ничего больше не содержит, то есть пустая
                            for del_ind in indexes_of_deleted_elements:
                                if not LRI_sorted_list[del_ind].r_p and not LRI_sorted_list[del_ind].i_p and not \
                                        LRI_sorted_list[del_ind].l_p:
                                    LRI_sorted_list.pop(del_ind)

                        intersection, t = status[index].is_cross(status[index + 1])
                        if intersection == Intersect.SKEW_CROSS and 0 < t < 1 + eps:
                            new_p = get_new_point(index, index + 1, t)
                            LRI_sorted_list.add(new_p)

                        intersection, t = status[index].is_cross(status[index - 1])
                        if intersection == Intersect.SKEW_CROSS and 0 < t < 1 + eps:
                            new_p = get_new_point(index, index - 1, t)
                            LRI_sorted_list.add(new_p)
    if get_additional_info:
        return answer, intersection_points, some_data

    return answer, intersection_points

"""
p_list, e_list = edge_generator(15)

# complex intersections for testing
M, L = [(100.25, 704), (50, 250), (650, 200), (100.25, 502), (500.25, 100), (400.25, 100), (200.25, 102), (400.25, 702),
        (100.25, 550), (400.25, 400), (300.25, 402.0), (600, 500)], \
       [[(100.25, 502), (300.25, 402.0)], [(50, 250), (650, 200)], [(300.25, 402.0), (400.25, 100)], [(300.25, 402.0), (600, 500)],
        [(100.25, 704), (500.25, 100)], [(200.25, 102), (400.25, 702)], [(100.25, 550), (400.25, 400)]]
p_list.extend(M)
e_list.extend(L)

O, P = [(100, 200), (900, 800), (300, 900), (700, 100), (100.25, 704), (500, 500), (300, 400), (700, 700)], \
       [[(100, 200), (900, 800)], [(300, 900), (700, 100)], [(100.25, 704), (500, 500)], [(300, 400), (700, 100)], [(700, 700), (700, 100)]]
p_list.extend(O)
e_list.extend(P)

# input data
print(p_list)
print(e_list)

# draw the initial graph

draw_graph(e_list, [], 0, 1000, 0, 1000)

# main algorithm
crossing_edges, crossing_points, data = bentli_ottman(e_list, 1)

# print result
for segment in crossing_edges:
    print(segment)

# draw the result graph
draw_graph(crossing_edges, crossing_points, 0, 1000, 0, 1000)


crossing_points = []
p_list, e_list = [(3, 1.5), (0.5, 0.5), (1.5, 1.5), (2, 2.5), (3, 2.5), (1, 1), (3, 1), (3, 3), (1, 3), (2, 2), (4, 2),
                  (2.75, 2), (3.25, 2), (3.25, 1.5), (2.75, 1.5)], [[(1, 3), (3, 1)], [(1, 1), (1, 3)],
                                                                    [(3, 3), (4, 2)], [(3, 1), (4, 2)],
                                                                    [(3.25, 2), (3.25, 1.5)], [(0.5, 0.5), (3, 3)],
                                                                    [(3.25, 1.5), (2.75, 1.5)],
                                                                    [(2.75, 1.5), (2.75, 2)], [(3, 1.5), (3, 2.5)],
                                                                    [(1.5, 1.5), (2, 2.5)], [(2, 2), (4, 2)]]
draw_graph(e_list, crossing_points, 0, 5, 0, 4)
crossing_edges, crossing_points, data = bentli_ottman(e_list, 1)
draw_graph(crossing_edges, crossing_points, 0, 5, 0, 4)
"""

