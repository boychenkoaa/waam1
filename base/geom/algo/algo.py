# список алгоритмов
from math import pi, sqrt, log10, tan, radians

from sortedcontainers import SortedList, SortedKeyList
from base.geom.algo.bentley import bentli_ottman, Edge
from base.geom.algo.buffer import buffer
from base.geom.algo.cut import cut_slice
from base.geom.primitives.geomgraph import GeomGraph
from base.geom.primitives.linear import *
from copy import copy, deepcopy

from base.geom.raw.raw import *

# from ngeom import distance_seg_p, distance_p_p
eps = EPSILON #  0.000001

# стрижка
# max_depth - максимальная глубина (после первой стрижки могут остаться вершины степени 1)
# None - резать до бесконечности, пока вершин степени 1 не останется


"""

def clip(gg: GeomGraph, max_depth=None):
    vert_for_clip = set()
    new_gg = GeomGraph()
    # заполняем список претендентов на удаление по степени вершины == 1
    for vert in gg.vertices:
        if self.deg_v(vert) == 1:
            vert_for_clip.add(vert)

    depth = 1
    while vert_for_clip:
        if max_depth and (depth > max_depth):
            break
        next_vert_for_clip = set()
        for vert in vert_for_clip:
            neigh = copy(self.get_neigh(vert)).pop()
            new_gg.add_s(self[vert], self[neigh])
            s = self._graph.deg_v(neigh)
            self.rem_id(vert)
            s = self._graph.deg_v(neigh)
            if self._graph.deg_v(neigh) == 1:
                next_vert_for_clip.add(neigh)
        vert_for_clip = next_vert_for_clip
        depth += 1
    return new_gg



class StraightSkeleton:
    def __call__(self, polygon: Polygon):
        ()
"""


# используется в get_pl_order
# пофиксить
def sequence(new_points, chain_edges, chain_num, additional_info, without_repeat):
    points_with_contour_nums = dict()
    main_seq = []  # порядок контуров
    visited = [chain_num]
    for ed in chain_edges:
        seq = SortedKeyList(key=lambda t_and_coord: t_and_coord[0])  # t_and_coord[0] = t param
        for point in new_points:
            t = Edge(ed).get_parametric_pos_of(point)
            if t is not None:
                seq.add([t, point])
                cross_pnt_with_info = additional_info[additional_info.bisect_key_left(point)]
                # знаем условный номер ломаной пользователя, хотим найти
                # номер контура в дополнительной информации о точке пересечения
                if point == cross_pnt_with_info[0]:
                    for cross_edge in cross_pnt_with_info[1]:
                        contour_num = cross_edge.get_info
                        if contour_num not in visited:
                            points_with_contour_nums[point] = contour_num
                            if without_repeat:
                                visited.append(contour_num)
        # знаем порядок точек на отрезке и имеем словарь: точка - номер её контура
        for point in seq:
            if points_with_contour_nums.get(point[1]) is not None:
                main_seq.append(points_with_contour_nums[point[1]])
    return main_seq


# протестировать с повторениями
def get_polyline_order(polyline_collection, user_edges, without_repeat=True):
    user_info = GeomGraph(user_edges)
    # user_info.make_geom_graph(user_edges)
    custom_points_face_num = len(polyline_collection)  # пусть всегда на последнем месте находится ломанная
    point_list = []
    arc_list = []
    arc_with_face = []
    for ind, obj in enumerate(polyline_collection):
        point_list.extend(obj.points())
        arc_list.extend(obj.segments())
        edge_and_face = list(map(lambda x: Edge(x, ind), obj.segments()))  # list(map(lambda x: [x, ind], obj.segments()
        arc_with_face.extend(edge_and_face)
    custom_chain_ind = custom_points_face_num
    point_list.extend(user_info.points)
    arc_list.extend(user_edges)
    edge_and_face = list(map(lambda x: Edge(copy(x), custom_chain_ind), user_edges))
    arc_with_face.extend(edge_and_face)
    new_edges, crossing_points, additional_info = bentli_ottman(arc_with_face, get_additional_info=True)
    pl_order = sequence(crossing_points, user_info.segments, custom_points_face_num, additional_info, without_repeat)
    return pl_order


def add_slice(s_list):
    new_s_list = []
    for pl in s_list:
        if len(pl) <= 2:
            new_s_list.append(pl)

    segment_list = list(filter(lambda seg: distance_pp(seg[0], seg[1]) > EPSILON, new_s_list))
    new_gg = GeomGraph(segment_list)
    poly_list, pline_list = cut_slice(new_gg)
    poly_list.extend(pline_list)
    return poly_list


def copy_geoms(input_geom_list, shear_vector: tuple):
    ans = []
    for input_geom in input_geom_list:
        new_geom = deepcopy(input_geom)
        new_geom.move_all(shear_vector)
        ans.append(new_geom)
    return ans


def custom_bisect_left(point_projection_dist, delta, init_dist, line_count):

    if point_projection_dist > init_dist:
        count = int((point_projection_dist - eps - init_dist) // delta)
        return count + 1 if count < line_count else line_count
    else:
        return 0


def custom_bisect_right(point_projection_dist, delta, init_dist, line_count):

    if point_projection_dist >= init_dist:
        count = int((point_projection_dist + eps - init_dist)//delta)
        return count + 1 if count < line_count else line_count
    else:
        return 0


def get_min_point_and_l_count(input_geom, slope_k, ctg_use, bead_width, initial_indent, line_count=None):
    if bead_width == 0:
        return [], None
    points_lists = input_geom.points()  # список точек
    b_gen_min = float("inf")
    b_gen_max = -float("inf")
    min_xy_gen = float("inf")
    points = []

    for list in points_lists:
        points.extend(list)

    for pnt in points:
        if ctg_use:
            b = pnt[0] - pnt[1] * slope_k
        else:
            b = pnt[1] - pnt[0] * slope_k

        if b < b_gen_min:
            b_gen_min = b
            min_xy_gen = pnt

        if b > b_gen_max:
            b_gen_max = b

    if line_count is None:  # тут аккуратно посмотреть EPSILON
        projected_bead_width = bead_width * sqrt(1 + slope_k * slope_k)
        projected_initial_indent = sqrt(1 + slope_k * slope_k) * initial_indent
        line_count = int((b_gen_max - b_gen_min - projected_initial_indent - EPSILON) // projected_bead_width) + 1  # максимальное количество
        return min_xy_gen, line_count
    else:
        return min_xy_gen


def get_cut_lines(input_geom, input_angle, bead_width, initial_indent=None, line_count=None):

    if initial_indent is None:
        initial_indent = bead_width / 2

    points = input_geom.points()
    ctg_use = (input_angle in range(45, 136)) or (input_angle in range(225, 316))

    slope_k = (1 / tan(radians(input_angle))) if ctg_use else tan(radians(input_angle))
    n_vec = (1, -slope_k) if ctg_use else (-slope_k, 1)
    n_vec_len = sqrt(n_vec[0] * n_vec[0] + n_vec[1] * n_vec[1])
    n_vec = (n_vec[0]/n_vec_len, n_vec[1]/n_vec_len)  # норомализация

    if line_count is None:
        glob_min_xy, line_count = get_min_point_and_l_count(input_geom, slope_k, ctg_use, bead_width, initial_indent)
    else:
        glob_min_xy = get_min_point_and_l_count(input_geom, slope_k, ctg_use, bead_width, initial_indent, line_count)

    if line_count == 0:
        return []

    dist_from_min_list = [initial_indent + x * bead_width for x in range(0, line_count)]

    x_0 = glob_min_xy[0]
    y_0 = glob_min_xy[1]

    line_count = len(dist_from_min_list)
    ans_dict = dict()
    for i, dist in enumerate(dist_from_min_list):
        ans_dict[i] = deepcopy(SortedKeyList(key=lambda x: (int_approximate(copy(x[0])), int_approximate(copy(x[1])))))  # тут тоже могут быть ошибки апроксимации при маленьком расстоянии между точками
    ans_lines = []

    for contour in points:
        # перенос точек полигона, попадающих на прямые
        for ind, point in enumerate(contour):
            # point_dist - расстояние от минимальной точки до прямой проходящей через данную точку
            point_projection_dist = (point[0] - x_0) * n_vec[0] + (point[1] - y_0) * n_vec[1]

            min_ind = custom_bisect_left(point_projection_dist, bead_width, initial_indent, line_count)
            max_ind = custom_bisect_right(point_projection_dist, bead_width, initial_indent, line_count)

            left_equality = (min_ind < len(dist_from_min_list)) and (abs(dist_from_min_list[min_ind] - point_projection_dist) < eps)
            right_equality = abs(dist_from_min_list[max_ind-1] - point_projection_dist) < eps
            if left_equality or right_equality:
                # если точка попала на прямую сдвигаем её на eps
                contour[ind] = (point[0] + 10 * eps * n_vec[0], point[1] + 10 * eps * n_vec[1])

        # заполнение словаря точками пересечения
        for i in range(len(contour) - 1):
            min_xy = contour[i]
            max_xy = contour[i+1]

            min_pnt_projection_dist = ((min_xy[0] - x_0) * n_vec[0] + (min_xy[1] - y_0) * n_vec[1])
            max_pnt_projection_dist = ((max_xy[0] - x_0) * n_vec[0] + (max_xy[1] - y_0) * n_vec[1])

            if min_pnt_projection_dist > max_pnt_projection_dist:
                min_pnt_projection_dist, max_pnt_projection_dist = max_pnt_projection_dist, min_pnt_projection_dist

            min_ind = custom_bisect_left(min_pnt_projection_dist, bead_width, initial_indent, line_count)
            max_ind = custom_bisect_right(max_pnt_projection_dist, bead_width, initial_indent, line_count)

            for i in range(min_ind, max_ind):
                width = (initial_indent + bead_width * i)
                d_x = width * n_vec[0]
                d_y = width * n_vec[1]
                line_vec = (slope_k, 1) if ctg_use else (1, slope_k)
                line_i = Line((x_0 + d_x, y_0 + d_y), line_vec)

                seg0 = Segment(min_xy, vec(min_xy, max_xy))
                itersect_point = intersect_sl(seg0, line_i)
                if itersect_point:  # вообще должна быть всегда, но на всякий случай оставлю проверку
                    ans_dict[i].add(itersect_point)

    # парсинг словаря, достаём полученные отрезки
    for i in ans_dict:
        for pnt in range(0, len(ans_dict[i]), 2):
            if ans_dict[i][pnt] != ans_dict[i][pnt + 1]:
                # добавляем сразу полилинии
                ans_lines.append(PLine([ans_dict[i][pnt], ans_dict[i][pnt + 1]]))
    return ans_lines





# poly1 = Polygon([(6, 1), (2, 2), (4, 5)], [[(4, 3), (4, 2), (3, 3)]])
# out = smart_buffer(input_geoms=[poly1], distance=-0.2)
# out2 = equidistant([poly1], bead_width=-0.2)
# b = 1

"""
a = Contour([(2, 3), (6, 3), (7, 1), (9, 6), (2, 6)])
# a2 = Contour([(12, 0), (12, 8), (19, 6), (20, 2)]) # Contour([(2, 1), (2, 7), (4, 7)])
# b = [-7, -6, -5, -3, -1, 0, 1, 2, 4]
# b = [0, 2, 5, 8, 10, 12, 14]
# b = [-1000000000 * 3, -1000000000 * 4, -1000000000 * 5, -1000000000*6, -1000000000*8, -1000000000*9, -1000000000*10]
# b = [1, 3, 4, 5, 6, 8]
k = 0
# sgmnts = a.segments()
b = get_poly_coeff_list(a, k, 1)

an = get_cut_lines(a, b, k)
n = 1
an = {list: 12} [[(12.0, 1.0), (16.0, 1.0)], [(6.5, 2.0), (7.4, 2.0)], [(12.0, 2.0), (20.0, 2.0)], [(6.0, 3.0), (7.8, 3.0)], [(12.0, 3.0), (19.75, 3.0)], [(2.0, 4.0), (8.2, 4.0)], [(12.0, 4.0), (19.5, 4.0)], [(2.0, 5.0), (8.6, 5.0)], [(12.0, 5.0), (19.25, 5.0)], [(2.0, 6.... View
a = Contour([(2, 6), (13, 6), (10, 2), (7, 5), (5, 1)]) 
b = PLine([(2, 6), (13, 6), (10, 2), (7, 5), (5, 1)])
new_p = get_nearest_point(a, (7, 7))
new_p_b = get_nearest_point(b, (7, 7))
p1 = cut(b, (7, 7))
p2 = cut(a, (7, 7))


b = Contour([(4, 9), (4, 7), (6, 7), (6, 9)])  # Contour([(5, 1), (6, 3), (5, 8), (7, 9), (9, 5)])
c = Contour([(9, 5), (2, 5), (2, 11), (9, 11)])  # Contour([(9, 10), (11, 7), (13, 9), (11, 11)])
e = Contour([(3, 6), (7, 6), (7, 10), (3, 10)])  # Contour([(3, 6), (7, 6), (7, 10), (3, 10)])
k1 = Contour([(16, 2), (16, 9), (22, 9), (22, 2)])
k2 = Contour([(17, 3), (17, 8), (21, 8), (21, 3)])
k3 = Contour([(18, 7), (18, 5), (20, 5), (20, 7)])
ordered_collection = [a, b, c, e, k1, k2, k3]



# обернуть в одну функцию, список ломаных, список отрезков и аргумент повтора
custom_input = [[(13, 6), (5, 8)], [(14, 6), (19, 6)], [(19, 6), (15, 10)]]  # [(13, 6), (19, 6)] , (7, 5), (12, 9), (3, 5)  # [(19, 6), (15, 10), (11, 2), (5, 8)]
no_repeats = True  # повторное посещение
order = get_polyline_order(ordered_collection, custom_input, no_repeats)
print(order)

# new_p = get_nearest_point(a, (8, 7))
b = 1

# точки введённые пользователем
# номер фэйса - индекс объекта в общем массиве

"""




