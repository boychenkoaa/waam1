
from sortedcontainers import SortedKeyList
import math
from enum import Enum

from base.geom.primitives.linear import Polygon
from points.CollisionDetector import IDEntity
from copy import deepcopy
from points.IDContainer import IDContainer
from base.tree import Forest
# from scipy.special import logsumexp

eps = 0.0001
alfa = 0.001


class VectorDirection(Enum):
    WAY_UP = 1
    WAY_DOWN = 2
    HORIZONTALLY = 3

# в value beg и end не должны входить

class HalfEdge(IDEntity):
    def __init__(self, beg, end, nxt, face_numb=None):
        val = {"begin": beg, "end": end, "next": nxt, "face_num": face_numb}
        super().__init__(id_=(beg, end), value=val)

    def __repr__(self):
        return "\n{}, next: {} face: {}".format((self.value["begin"], self.value["end"]), (self.value["end"], self.value["next"]), self.value["face_num"])

    def edge(self):
        return (self.value["begin"], self.value["end"])

    def next_edge(self):
        return (self.value["end"], self.value["next"])

    def face(self):
        return self.value["face_num"]

    def set_face(self, f_n):
        self.value["face_num"] = f_n

    def set_next(self, next_v_n):
        self.value["next"] = next_v_n

    def __eq__(self, other):
        return (self.value["begin"] == other.value["begin"]) and (self.value["end"] == other.value["end"]) # abs(self.begin - other.begin) < eps

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return (self.value["begin"] < other.value["begin"]) or ((self.value["begin"] == other.value["begin"]) and (self.value["end"] < other.value["end"]))

    def __gt__(self, other):
        return (self.value["begin"] > other.value["begin"]) or ((self.value["begin"] == other.value["begin"]) and (self.value["end"] > other.value["end"]))


def polar_edge(x, y):
    fi = 0
    if x > 0:
        if y >= 0:
            fi = math.atan( y /x)
        else:
            fi = math.atan(y / x) + 2 * math.pi
    elif x == 0:
        if y > 0:
            fi = math.pi / 2
        elif y < 0:
            fi = 3 * math.pi / 2
    else:
        fi = math.atan(y / x) + math.pi
    return fi


def get_x(edge, y):
    if abs(edge[0][1] - edge[1][1]) < eps:
        return edge[1][0]
    return edge[0][0] + (edge[1][0] - edge[0][0]) * (y - edge[0][1]) / (edge[1][1] - edge[0][1])


def convert_to_polar_and_sort(geom_graph, vert, neighbour_points_id):
    point = geom_graph[vert]
    neighbour_points_and_ids = list(map(lambda x: (geom_graph[x], x), neighbour_points_id))
    # тут надо перевести систему координат так, чтобы её центр был в точке vert
    sorted_neigh = SortedKeyList(key=lambda x: polar_edge(x[0][0], x[0][1]))
    # сортировка
    for point_and_id in neighbour_points_and_ids:
        neigh_in_new_coord = (point_and_id[0][0] - point[0], point_and_id[0][1] - point[1])
        sorted_neigh.add((neigh_in_new_coord, point_and_id[1]))
    # достаём сортированные id соседних точек
    id_sorted_by_edge = list(map(lambda pnt_and_id:  pnt_and_id[1],  sorted_neigh))
    return id_sorted_by_edge


def det(x1, y1, x2, y2, x3, y3):
    return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)


def check_cw_bypas(contour):
    min_x_point = contour[0]
    min_ind = 0
    for i in range(len(contour) - 1):
        if contour[i] < min_x_point:
            min_x_point = contour[i]
            min_ind = i
    return True if det(contour[min_ind][0], contour[min_ind][1], contour[min_ind - 1][0], contour[min_ind - 1][1], contour[min_ind + 1][0], contour[min_ind + 1][1]) > 0 else False


class DCEL:
    __slots__ = ('_base_gg', 'neighbour_list', 'half_edge_list', 'face_list')

    def __init__(self, base_graph):  # на вход подаётся планарный геом.граф
        # Нужен список вершин + id - points в геом. графе
        # список полу рёбер + след ребро + № face
        # список face-ов: id + представитель + (представ. дырок)
        def cross_ray(h_ed, c_face_id):
            point_of_cross = False
            # существует ли пересечение двух отрезков ed и y = geom_graph.get_point(face_list[c_face_id][1][1])[1]
            # левее, чем geom_graph.get_point(face_list[c_face_id][0][1])[0] = x - координате точки пересечения
            # отрезок
            edge = h_ed.edge()
            point_no = self.face_list[c_face_id][1][1]
            x_y = self[point_no]
            up = self[edge[0]]
            down = self[edge[1]]
            if down[1] > up[1]:
                up, down = down, up
            if x_y[1] > up[1] or x_y[1] < down[1] or (up[0] >= x_y[0] and down[0] >= x_y[0]):
                return point_of_cross  # точки пересечения точно нет
            else:
                # точка пересечения точно есть
                x_new = down[0] + ((x_y[1] - down[1]) * (up[0] - down[0])) / (up[1] - down[1] + eps)
                if x_new >= x_y[0]:  # возможно просто > !!!
                    return point_of_cross
                point_of_cross = (x_new, x_y[1])
            return point_of_cross

        def rays_crossing(face_id_list):  # face_id_list - внешние контура
            answer = {}  # словарь: ключ - id внешнего фэйса, значение - ближайшая левая точка
            connectivity_comp = dict()  # - заполнить самими левыми точками фэйсов из face_id_list
            n_inf = float('-inf')
            connectivity_comp[face_id_list[0]] = -1
            for i in range(1, len(face_id_list)):  # итерация по y лучам, 0-ой не исследуем, он равен бесконечности
                answer[face_id_list[i]] = (n_inf, n_inf)

                for half_edge in self.half_edge_list:
                    # если луч пересекается, то обновляем для него ответ
                    # answer[face_id] - x-координата точки пересечения ребра
                    # и горизонтального луча из самой левой точки внешнего фэйса
                    point = cross_ray(half_edge, face_id_list[i])  # тут только вычисления точки пересечения
                    if point:
                        if answer[face_id_list[i]][0] < point[0]:  # сравниваем x
                            # если точка найдена и она по x больше, чем предыдущая
                            answer[face_id_list[i]] = point
                            connectivity_comp[face_id_list[i]] = half_edge.face()
                        elif answer[face_id_list[i]] == point:  # если точки совпали, возможно с точностью до eps
                            # тут сравниваем направление, сохраняем то ребро, что идёт вниз
                            # какому ребру принадлежат точки - ?
                            # найти координаты концов ребра, сравнить y начала и конца
                            # если y конца меньше, то это искомое ребро
                            edge = half_edge.edge()
                            if self[edge[0]][1] > self[edge[1]][1]:  # сравниваем координаты
                                answer[face_id_list[i]] = point
                                connectivity_comp[face_id_list[i]] = half_edge.face()
                if answer[face_id_list[i]] == (n_inf, n_inf):
                    connectivity_comp[face_id_list[i]] = -1
            return connectivity_comp

        # оставить ли тут проверку на пустоту графа?
        if base_graph is not None and not base_graph.is_empty():
            geom_graph = deepcopy(base_graph)
            # geom_graph = geom_graph.make_pslg()
            p_v = geom_graph.get_pendant_v()
            i_v = geom_graph.get_isolated_v()
            assert len(p_v) == 0 and len(i_v) == 0
            self._base_gg = geom_graph
            vert_list = geom_graph.vertices
            self.neighbour_list = {}
            for vert in vert_list:
                # для обеих сторон ищем обход
                neigh = geom_graph.get_neigh(vert)
                # список соседних точек, надо отсортировать по углу
                sort_neigh = convert_to_polar_and_sort(geom_graph, vert, neigh)
                # надо получить список id соседних рёбер
                self.neighbour_list[vert] = sort_neigh
            arc_list = self._base_gg.arcs  # список полурёбер надо добавить к каждому следующее ребро и номер фэйса
            # итерация по полурёбрам
            # находим следующее ребро для всех рёбер
            self.half_edge_list = IDContainer()
            for ed in arc_list:
                beg = ed[0]
                end = ed[1]
                search_index = self.neighbour_list[end].index(beg) - 1
                self.half_edge_list.add(HalfEdge(beg, end, self.neighbour_list[end][search_index]))
                # хотим найти точку, к которой замыкается цикл, последовательно переходим по рёбрам
            self.face_list = {}
            face_id = -1
            # список внешних фэйсов, отсортированный по y самой левой точки
            external_face_list = SortedKeyList(key=lambda f_id: geom_graph[(self.face_list[f_id][0][1])])
            ed_list = deepcopy(self.half_edge_list)
            while len(ed_list):
                full_cycle = False
                first_half_edge = ed_list.pop()  # зафиксировали стартовое ребро
                first_arc = first_half_edge.edge()
                next_arc = first_half_edge.next_edge()  # следующее за ним
                min_x_arc = first_arc  # поиск полуребра с минимальным началом
                # читаем по одной
                face_id += 1  # добавить к полурёбрам

                # устанавливаем фэйс для первого прочитанного полуребра
                self.half_edge_list[first_arc].set_face(face_id)
                while not full_cycle:  # пока не сделаем полный обход
                    if next_arc != first_arc:
                        # устанавливаем фэйс для текущего полуребра
                        self.half_edge_list[next_arc].set_face(face_id)
                        # удаляем его из списка полурёбер
                        ed_list.rem(next_arc)
                        # надо сравнивать по значению, а не по id
                        next_point = geom_graph[next_arc[1]]
                        # левейшая точка - конец вектора, идущего в точку с минимальной x-координатой
                        leftest_point = geom_graph[min_x_arc[1]]
                        if (leftest_point[0] - next_point[0] > eps) or (abs(next_point[0] - leftest_point[0]) < eps) and \
                                (leftest_point[1] - next_point[1] > eps):
                            min_x_arc = next_arc
                    else:
                        full_cycle = True
                    # читаем следующее полуребро
                    next_arc = self.half_edge_list[next_arc].next_edge()
                self.face_list[face_id] = [min_x_arc]
                # рассматриваем (A[i], A[i+1]) и  (A[i], A[i-1])
                prev_ind = min_x_arc[0]
                min_ind = min_x_arc[1]
                next_ind = self.half_edge_list[min_x_arc].next_edge()[1]

                d_pas = det(geom_graph[min_ind][0], geom_graph[min_ind][1], geom_graph[prev_ind][0],
                            geom_graph[prev_ind][1], geom_graph[next_ind][0], geom_graph[next_ind][1])
                is_it_external = True if d_pas >= 0 else False
                if is_it_external:
                    external_face_list.add(face_id)
                # тут временно добавили нулевой элемент - маркер того, является ли фэйс внешним
                self.face_list[face_id].insert(0, is_it_external)
            self.face_list[-1] = [False, (-1, -1)]
            if len(external_face_list) == 0:
                # это не пплг, а линия
                print("error, this is line, not dcel")
                # print(self._base_gg.segments)
                # print(self.face_list)
            else:

                # print(self.half_edge_list)
                # нужен список ближайших найденных левых соседей для каждой точки из самых левых точек external_face_list
                adjacency_list = rays_crossing(external_face_list)

                f_n = list(set(adjacency_list.values()).union(set(adjacency_list.keys())))

                f = Forest(nodes=f_n)
                for key, value in adjacency_list.items():
                    f.move(int(key), value)
                tr_w_r = [f.dfs(child) for child in f.children(None)]

                for tree in tr_w_r:
                    root = tree.pop(0)
                    for leave in tree:  # меняем face_list
                        hole = self.face_list[leave][1]
                        self.face_list[root].append(hole)
                        self.half_edge_list[hole].set_face(root)
                        self.face_list.pop(leave)
                        next_n = self.half_edge_list[hole].next_edge()
                        while next_n != hole:
                            self.half_edge_list[next_n].set_face(root)
                            next_n = self.half_edge_list[next_n].next_edge()

            self.half_edge_list.add(HalfEdge(-1,  -1, -1, -1))  # добавим бесконечное ребро
            for face in self.face_list.values():  # итерация по словарю
                face.pop(0)

    def __getitem__(self, item):
        return self._base_gg[item]

    def find(self, point):
        return self._base_gg.find(point)

    def get_segment(self, edge):
        segment = [self[edge[0]], self[edge[1]]]
        return segment

    def edge_direction(self, edge):
        """
        edge is considered as a vector
        compare by y-coordinate
        with epsilon precision
        """
        begin = self[edge[0]]
        end = self[edge[1]]
        if begin[1] - end[1] > eps:
            return VectorDirection.WAY_DOWN
        elif end[1] - begin[1] > eps:
            return VectorDirection.WAY_UP
        else:
            return VectorDirection.HORIZONTALLY

    def __repr__(self):
        return "neighbour list: {}\nfaces and their representatives: {}\ngraph half-edges: {}".format(
            self.neighbour_list, self.face_list, self.half_edge_list)

    def check_vertex_deg(self):
        return self._base_gg.is_contours()

    def nesting_tree(self):
        # список первых рёбер внешних контуров,
        # если есть дырки, то они дописываются в виде рёбер представителей после контура
        nesting_tree = False
        # print(self.check_vertex_deg())
        if self.check_vertex_deg():  #
            nesting_tree = []
            # построить список внешняя: внутренняя грань
            faces_for_review = [[(-1, -1), 0]]  # представители фэйсов
            while len(faces_for_review) > 0:
                current_face = faces_for_review.pop(0)
                current_edge = current_face[0]
                level = current_face[1]
                if level % 2 == 1:  # если мы на нечётном уровне
                    nesting_tree.append([(current_edge[1], current_edge[0])])
                elif level != 0:
                    parent = current_face[2]  # номер родителя
                    nesting_tree[parent].append((current_edge[1], current_edge[0]))
                # считываем очередную грань
                face = self.half_edge_list[current_edge].face()
                count_of_holes = len(self.face_list[face]) - 1
                if count_of_holes > 0:
                    level += 1  # погружаемся на уровень ниже
                    for hole_num in range(0, count_of_holes):
                        edge = self.face_list[face][hole_num + 1]
                        reversed_edge = (edge[1], edge[0])
                        if level % 2 == 0:
                            parent = len(nesting_tree) - 1
                            faces_for_review.append([reversed_edge, level, parent])
                        else:
                            faces_for_review.append([reversed_edge, level])
        return nesting_tree

    def get_contour_by_edge(self, ed):  # поточечный контур
        if ed == (-1, -1):
            return None
        contour = [self[ed[0]]]
        next_ed = self.half_edge_list[ed].next_edge()
        while ed != next_ed:
            contour.append(self[next_ed[0]])
            next_ed = self.half_edge_list[next_ed].next_edge()
        contour.append(self[ed[0]])
        return contour

    def get_face_contours(self, face_num, external_only=False):  # возможно внещние - ?
        contours = []
        eds = self.face_list[face_num]
        if external_only:
            contours = [self.get_contour_by_edge(eds[0])]
            return contours
        for ed in eds:
            cont = self.get_contour_by_edge(ed)
            contours.append(cont)
        return contours

    def get_all_contours(self, external_only=False, without_none=True):  # поточечные контуры
        contours = []
        for face_num in self.face_list.keys():  # итерация по словарю
            contours_list = self.get_face_contours(face_num, external_only)
            contours.extend(contours_list)
        if without_none:
            contours = list(filter(lambda cont: cont is not None, contours))
        return contours

    def get_polygons_list(self):
        tree_list = self.nesting_tree()
        polygon_list = []
        if tree_list:
            for val in tree_list:
                holes = []
                contour = []
                hole_flag = False
                while val:
                    if hole_flag:
                        hole = []
                        ind = val.pop(0)
                        point = self[ind[0]]
                        hole.append(point)
                        next_ind = self.half_edge_list[ind].next_edge()
                        next_point = self[next_ind[0]]
                        while point != next_point:
                            hole.append(next_point)
                            next_ind = self.half_edge_list[next_ind].next_edge()
                            next_point = self[next_ind[0]]
                        holes.append(hole)
                    else:
                        hole_flag = True
                        ind = val.pop(0)
                        point = self[ind[0]]
                        contour.append(point)
                        next_ind = self.half_edge_list[ind].next_edge()
                        next_point = self[next_ind[0]]
                        while point != next_point:
                            contour.append(next_point)
                            next_ind = self.half_edge_list[next_ind].next_edge()
                            next_point = self[next_ind[0]]
                poly = Polygon(contour, holes)
                polygon_list.append(poly)
            return polygon_list
        else:
            return []

    def move_all(self, vector: tuple):
        self._base_gg.move_all(vector)

    def convert_to_gg(self):
        return self._base_gg


"""
v = [(1, 1), (3, 1), (3, 3), (1, 3), (2, 2), (4, 2), (2.75, 2), (3.25, 2), (3.25, 1.5), (2.75, 1.5)]
e = [[(1, 1), (3, 3)], [(1, 3), (3, 1)], [(2, 2), (4, 2)], [(1, 1), (1, 3)], [(3, 3), (4, 2)], [(3, 1), (4, 2)],
     [(3.25, 2), (3.25, 1.5)], [(3.25, 1.5), (2.75, 1.5)], [(2.75, 1.5), (2.75, 2)]]
e = [[(1, 1), (13, 1)], [(1, 10), (13, 10)], [(1, 1), (1, 10)], [(13, 10), (13, 1)],
     [(2, 2), (6, 2)], [(6, 2), (6, 9)], [(6, 9), (2, 9)], [(2, 9), (2, 2)],
     [(3, 3), (5, 3)], [(5, 3), (5, 8)], [(5, 8), (3, 8)], [(3, 8), (3, 3)],
     [(3.5, 4), (4.5, 4)], [(4.5, 4), (4.5, 5)], [(4.5, 5), (3.5, 5)], [(3.5, 5), (3.5, 4)],
     [(3.5, 6.5), (4.5, 6.5)], [(4.5, 6.5), (4.5, 7.5)], [(4.5, 7.5), (3.5, 7.5)], [(3.5, 7.5), (3.5, 6.5)],
     [(8, 4), (12, 4)], [(12, 4), (12, 9)], [(12, 9), (8, 9)], [(8, 9), (8, 4)],
     [(9, 6), (10, 6)], [(10, 6), (10, 8)], [(10, 8), (9, 8)], [(9, 8), (9, 6)],
     [(9.5, 4.5), (10.5, 4.5)], [(10.5, 4.5), (10.5, 5.5)], [(10.5, 5.5), (9.5, 5.5)], [(9.5, 5.5), (9.5, 4.5)]]
gr1 = GeomGraph(e)
ver = gr1.vertices
arc = gr1.edges
bentley.draw_graph(gr1.segments, [])
gr2 = gr1.make_pslg()
graph2 = DCEL(gr2)
check = graph2.check_vertex_deg()
cnt = graph2.get_all_contours()  # get_all_contours()
# bentley.draw_graph(gr2.segments, [], 0, 5, 0, 4)
t1 = gr2.has_segment((1, 1), (3, 3))
t2 = gr2.has_segment((2, 2), (1, 1))
gr2.rem_s((2, 2), (2.75, 2))
gr2.rem_s((3.25, 2), (4, 2))
# bentley.draw_graph(gr2.segments, [], 0, 5, 0, 4)


v = [(1, 1), (13, 1), (1, 10), (13, 10),
     (2, 2), (6, 2), (6, 9), (2, 9),
     (3, 3), (5, 3), (5, 8), (3, 8),
     (3.5, 4), (4.5, 4), (4.5, 5), (3.5, 5),
     (3.5, 6.5), (4.5, 6.5), (4.5, 7.5), (3.5, 7.5),
     (8, 4), (12, 4), (12, 9), (8, 9),
     (9, 6), (10, 6), (10, 8), (9, 8),
     (9.5, 4.5), (10.5, 4.5), (10.5, 5.5), (9.5, 5.5)]

e = [[(1, 1), (13, 1)], [(1, 10), (13, 10)], [(1, 1), (1, 10)], [(13, 10), (13, 1)],
     [(2, 2), (6, 2)], [(6, 2), (6, 9)], [(6, 9), (2, 9)], [(2, 9), (2, 2)],
     [(3, 3), (5, 3)], [(5, 3), (5, 8)], [(5, 8), (3, 8)], [(3, 8), (3, 3)],
     [(3.5, 4), (4.5, 4)], [(4.5, 4), (4.5, 5)], [(4.5, 5), (3.5, 5)], [(3.5, 5), (3.5, 4)],
     [(3.5, 6.5), (4.5, 6.5)], [(4.5, 6.5), (4.5, 7.5)], [(4.5, 7.5), (3.5, 7.5)], [(3.5, 7.5), (3.5, 6.5)],
     [(8, 4), (12, 4)], [(12, 4), (12, 9)], [(12, 9), (8, 9)], [(8, 9), (8, 4)],
     [(9, 6), (10, 6)], [(10, 6), (10, 8)], [(10, 8), (9, 8)], [(9, 8), (9, 6)],
     [(9.5, 4.5), (10.5, 4.5)], [(10.5, 4.5), (10.5, 5.5)], [(10.5, 5.5), (9.5, 5.5)], [(9.5, 5.5), (9.5, 4.5)]]



v = [(2, 9), (4, 2), (4, 15), (13, 15),
     (15, 9), (13, 2), (19, 2), (19, 15),
     (4, 4), (4, 13), (12, 13), (12, 4),
     (5, 9), (5, 12), (8, 12), (8, 9),
     (9, 5), (9, 7), (11, 5), (11, 7),
     (20, 1), (20, 14), (30, 14), (30, 1),
     (21, 8), (25, 8), (21, 13), (25, 13),
     (22, 9), (24, 9), (22, 12), (24, 12),
     (25, 3), (25, 7), (29, 7), (29, 3),
     (26, 4), (26, 6), (28, 6), (28, 4)]

e = [[(2, 9), (4, 2)], [(2, 9), (4, 15)], [(4, 15), (13, 15)], [(13, 15), (15, 9)], [(15, 9), (13, 2)],
     [(13, 2), (4, 2)], [(13, 2), (19, 2)], [(15, 9), (19, 2)], [(15, 9), (19, 15)], [(13, 15), (19, 15)],
     [(4, 4), (4, 13)], [(12, 13), (4, 13)], [(12, 13), (12, 4)], [(4, 4), (12, 4)], [(12, 13), (4, 4)],
     [(5, 9), (5, 12)], [(5, 9), (8, 9)], [(5, 12), (8, 12)], [(8, 12), (8, 9)],
     [(9, 5), (9, 7)], [(9, 7), (11, 7)], [(9, 5), (11, 5)], [(11, 5), (11, 7)],
     [(20, 1), (20, 14)], [(20, 1), (30, 14)], [(20, 1), (30, 1)], [(20, 14), (30, 14)], [(30, 14), (30, 1)],
     [(21, 8), (25, 8)], [(25, 8), (25, 13)], [(21, 13), (25, 13)], [(21, 13), (21, 8)],
     [(22, 9), (24, 9)], [(24, 9), (24, 12)], [(22, 12), (24, 12)], [(22, 12), (22, 9)],
     [(25, 3), (25, 7)], [(25, 7), (29, 7)], [(29, 7), (29, 3)], [(29, 3), (25, 3)],
     [(26, 4), (26, 6)], [(26, 6), (28, 6)], [(28, 6), (28, 4)], [(28, 4), (26, 4)]]


v = [(2, 2), (3, 3), (10, 2), (2, 9), (10, 9), (5, 3), (5, 5), (3, 5), (7, 3), (9, 3), (7, 5),
     (9, 5), (4, 6), (4, 8), (6, 6), (6, 8), (3.5, 3.5), (3.5, 4.5), (4.5, 3.5), (4.5, 4.5)]


e = [[(1, 1), (13, 1)], [(1, 10), (13, 10)], [(1, 1), (1, 10)], [(13, 10), (13, 1)],
     [(2, 2), (6, 2)], [(6, 2), (6, 9)], [(6, 9), (2, 9)], [(2, 9), (2, 2)],
     [(3, 3), (5, 3)], [(5, 3), (5, 8)], [(5, 8), (3, 8)], [(3, 8), (3, 3)],
     [(3.5, 4), (4.5, 4)], [(4.5, 4), (4.5, 5)], [(4.5, 5), (3.5, 5)], [(3.5, 5), (3.5, 4)],
     [(3.5, 6.5), (4.5, 6.5)], [(4.5, 6.5), (4.5, 7.5)], [(4.5, 7.5), (3.5, 7.5)], [(3.5, 7.5), (3.5, 6.5)],
     [(8, 4), (12, 4)], [(12, 4), (12, 9)], [(12, 9), (8, 9)], [(8, 9), (8, 4)],
     [(9, 6), (10, 6)], [(10, 6), (10, 8)], [(10, 8), (9, 8)], [(9, 8), (9, 6)],
     [(9.5, 4.5), (10.5, 4.5)], [(10.5, 4.5), (10.5, 5.5)], [(10.5, 5.5), (9.5, 5.5)], [(9.5, 5.5), (9.5, 4.5)]]
e = [[(2, 2), (10, 2)], [(10, 2), (10, 9)], [(2, 2), (2, 9)], [(2, 9), (10, 9)], [(3, 3), (5, 3)], [(3, 3), (3, 5)],
     [(5, 5), (3, 5)], [(5, 5), (5, 3)], [(7, 3), (9, 3)], [(7, 5), (9, 5)], [(7, 5), (7, 3)], [(9, 5), (9, 3)],
     [(4, 6), (4, 8)], [(6, 6), (6, 8)], [(4, 8), (6, 8)], [(4, 6), (6, 6)], [(3.5, 3.5), (3.5, 4.5)], [(3.5, 4.5), (4.5, 4.5)], [(4.5, 4.5), (4.5, 3.5)], [(4.5, 3.5), (3.5, 3.5)]]
"""

