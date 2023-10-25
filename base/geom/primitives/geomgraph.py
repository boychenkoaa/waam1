from base.geom.raw.raw import EPSILON, distance_pp
from base.graph import Graph
from points.points import SmartPoints
from copy import copy
from base.geom.primitives.linear import PLine


class iCollisionDetector:
    def __init__(self):
        pass

    def add(self, id_, point):
        pass

    def rem(self, id_):
        pass

    def __contains__(self, point):
        pass

    def find(self, point):
        pass


# фасад для обычного графа и точек
class iGeomGraph:
    def __init__(self):
        pass

    def add_p(self, point):
        pass

    def add_e(self, edge):
        pass

    def _rem_p(self, point):
        pass

    def rem_id(self, id_):
        pass

    def rem_e(self, edge):
        pass

    def make_planar(self):
        pass

    def __repr__(self):
        pass


class GeomGraph(iGeomGraph):
    __slots__ = ["_points", "_graph", "is_pslg"]

    def __init__(self, segment_list: list = None, point_list: list = None):
        super().__init__()
        self._points = SmartPoints()
        self._graph = Graph()
        if segment_list is not None:
            for segment in segment_list:
                if not self.has_segment(segment[0], segment[1]) and distance_pp(segment[0], segment[1]) > EPSILON:
                    self.add_s(segment[0], segment[1])  # уже добавляет точки

        if point_list is not None:  # опциональный параметр добавления отдельных точек
            for point in point_list:
                self.add_p(point)
        self.is_pslg = False

    def add_segments(self, segment_list: list):
        for segment in segment_list:
            self.add_s(segment[0], segment[1])
        self.is_pslg = False

    def raw(self):  # проверить
        points_and_graph = {"points": self._points.raw(), "graph": self._graph.edges}
        return points_and_graph

    def __getitem__(self, id_):
        return self._points[id_].value

    def get_neigh(self, id_):  # соседние вершины по id
        return self._graph[id_]

    def find(self, point):
        point_id = self._points.find(point)
        return point_id

    def deg(self, id_):
        return self._graph.deg_v(id_)

    def add_p_to_edge_center(self, id1, id2):
        assert self._graph.has_e([id1, id2])
        point_x = (self[id1][0] + self[id2][0]) / 2
        point_y = (self[id1][1] + self[id2][1]) / 2

        c_id = self._points.add((point_x, point_y))
        if not self._graph.has_v(c_id):
            self._graph.add_v(c_id)
        self.rem_arc([id1, id2])
        self.add_e([id1, c_id])
        self.add_e([id2, c_id])
        return c_id

    """
    def rem_id_with_connecting(self, c_id):
        self._graph.rem_v(c_id)
        self._points.rem(c_id)
    """

    def add_p(self, point):
        new_id = self._points.add(point)
        if not self._graph.has_v(new_id):
            self._graph.add_v(new_id)
        self.is_pslg = False
        return new_id

    def add_by_id(self, new_id, point):
        self._points.add_by_id(new_id, point)
        self._graph.add_v(new_id)
        self.is_pslg = False

    def add_s(self, point1, point2):
        new_id1 = self.add_p(point1)
        new_id2 = self.add_p(point2)
        if not self.has_edge(new_id1, new_id2):
            self._graph.add_e([new_id1, new_id2])
        return [new_id1, new_id2]

    def add_e(self, edge):  # между существующими точками
        self._graph.add_e(edge)

    def rem_id(self, id_):
        # удалить все соседние рёбра, безопасность осуществляется глубже
        self._graph.rem_v(id_)
        self._points.rem(id_)

    def _rem_p(self, point):  # переделать в remove_by_point
        p_id = self._points.find(point)
        if p_id:  # чтобы не передавать None дальше
            self.rem_id(p_id)

    def rem_e(self, edge):  # удаление вместе с вершинами
        self.rem_id(edge[0])
        self.rem_id(edge[1])

    def rem_arc(self, edge):  # удаление только отрезка между вершинами
        self._graph.rem_e(edge)

    def rem_s(self, point1, point2):
        id1 = self.find(point1)
        id2 = self.find(point2)
        self._graph.rem_e((id1, id2))
        # тут удаляем только если больше нет рёбер выходящих из этих точек
        if self._graph.deg_v(id1) == 0:
            self.rem_id(id1)
        if self._graph.deg_v(id2) == 0:
            self.rem_id(id2)

    def move_id(self, id_, new_xy: tuple):
        # поменять координату в хранилище, проверить!!
        self._points.move(id_, new_xy)

    def move_p(self, point, new_x, new_y):
        p_id = self._points.find(point)
        if p_id is not None:
            self.move_id(p_id, (new_x, new_y))

    def move_all(self, vector: tuple):
        self._points.move_all(vector)

    def has_edge(self, vert1_id, vert2_id):  # find vs has , has = find == 0
        if self._graph.has_e([vert1_id, vert2_id]):
            return [self._points[vert1_id], self._points[vert2_id]]
        else:
            return None

    def has_segment(self, point1, point2):
        id1 = self.find(point1)
        id2 = self.find(point2)
        return self._graph.has_e([id1, id2])

    def is_empty(self):
        return self._graph.is_empty()

    @property
    def edges(self):
        return self._graph.edges

    @property
    def arcs(self):
        return self._graph.arcs

    @property
    def segments(self):
        return [[self._points[begin].value, self._points[end].value] for begin, end in self.edges]

    @property
    def vertices(self):
        return self._graph.vertices

    @property
    def points(self):
        return self._points.p_list()

    def is_contours(self):  # is_contours  переименовать
        for vert in self._graph.vertices:
            if self._graph.deg_v(vert) != 2:
                return False
        return True

    def get_isolated_v(self):
        return self._graph.get_isolated_v()

    def del_isolated_v(self):
        self._graph.del_isolated_v()

    def get_pendant_v(self):
        return self._graph.get_pendant_v()

    def clipping(self, deg=0):
        vert_for_clip = set()
        already_clip = set()
        new_gg = GeomGraph()
        for vert in self._graph.vertices:
            if self._graph.deg_v(vert) == 1:
                vert_for_clip.add(vert)
        # print(vert_for_clip)
        deg_count = 1
        while vert_for_clip:
            if (deg != 0) and (deg_count > deg):
                break
            next_vert_for_clip = set()
            for vert in vert_for_clip:
                if len(self.get_neigh(vert)) == 0:
                    self.rem_id(vert)  # тут удаляются id у исходного графа и никуда не записываются!!!!
                    already_clip.add(vert)
                    # print(vert)
                    continue
                neigh = self._graph[vert].pop()
                new_gg.add_s(self[vert], self[neigh])
                self.rem_id(vert)  # тут удаляются id у исходного графа и никуда не записываются!!!!
                already_clip.add(vert)

                if (self._graph.deg_v(neigh) == 1) and (neigh not in vert_for_clip) and (neigh not in next_vert_for_clip) and (neigh not in already_clip):
                    next_vert_for_clip.add(neigh)
            vert_for_clip = next_vert_for_clip
            deg_count += 1
        return new_gg

    def get_comps(self):  # возвращает список графов, каждый из которых состоит из связанных вершин
        con_components = self._graph.get_connectivity_components()
        graph_list = []
        for com in con_components:
            edges_coords = []
            edges = com[1]
            for ed in edges:
                edges_coords.append([self[ed[0]], self[ed[1]]])
            graph_list.append(GeomGraph(edges_coords))
        return graph_list

    # возможно вынести из геом графа и добавить в обычный граф,
    def partition(self):  # разделение паукообразного графа на части со степенями у всех вершин не больше 2
        gg_list = []
        pline_list = []
        for vert in self._graph.vertices:
            if self._graph.deg_v(vert) > 2:  # разрезаем на линии
                neigh = self.get_neigh(vert)
                for n_vrt in neigh:
                    # добавляем все отростки в разные геом графы
                    gg = GeomGraph()
                    temp_vert = copy(vert)

                    point_list = [self[temp_vert]]
                    while True:
                        gg.add_s(copy(self[n_vrt]), copy(self[temp_vert]))  # добавили одно ребро
                        point_list.append(self[n_vrt])
                        if self._graph.deg_v(n_vrt) == 1:
                            break
                        new_neigh = self.get_neigh(n_vrt)
                        new_neigh.remove(temp_vert)  # тут всегда две вершины
                        temp_vert = copy(n_vrt)
                        n_vrt = copy(new_neigh.pop())
                    gg_list.append(gg)
                    pl = PLine(point_list)
                    pline_list.append(pl)
        if not gg_list:
            current_vert = []
            pline = []
            prev_vert = None
            gg_list.append(self)
            not_end = False
            for vt in copy(self._graph.vertices):
                if self._graph.deg_v(vt) == 1:
                    current_vert = vt
                    not_end = True
                    break
            while not_end:
                pline.append(copy(self[current_vert]))
                new_neigh = self.get_neigh(current_vert)
                new_neigh.discard(prev_vert)
                if new_neigh:
                    prev_vert = copy(current_vert)
                    current_vert = copy(new_neigh.pop())
                else:
                    not_end = False
            if pline:
                pline_list.append(PLine(pline))
        return gg_list, pline_list  # отдаёт список геомграфов и список соответствующих им ломанных

    def __str__(self):
        return "Vertices" + str(self.vertices) + "\n" + \
            "segments" + str(self.segments)

    def __repr__(self):
        return str(self)




# v = [(1, 1), (3, 1), (3, 3), (1, 3), (2, 2), (4, 2), (2.75, 2), (3.25, 2), (3.25, 1.5), (2.75, 1.5)]
# e = [[(1, 1), (3, 3)], [(1, 3), (3, 1)], [(2, 2), (4, 2)], [(1, 1), (1, 3)], [(3, 3), (4, 2)], [(3, 1), (4, 2)],
     # [(3.25, 2), (3.25, 1.5)], [(3.25, 1.5), (3.1, 1.3)], [(3.1, 1.3), (3.02, 1.3)],  [(3.25, 1.5), (2.9, 1.3)], [(2.9, 1.3), (3.0, 1.3)], [(3.25, 1.5), (3.2, 1.3)], [(3.25, 1.5), (2.75, 1.5)], [(2.75, 1.5), (2.75, 2)]]
# e = [[(9.941972502780326, 51.408150886856774), (3.4090620080494975, 48.66726613399517)], [(9.941972502780326, 51.408150886856774), (9.941971557276183, 24.10065829577791)], [(3.4090620080494975, 48.66726613399517), (2.8786696441184967, 48.44473916721805)], [(9.941971557276183, 24.10065829577791), (9.941974207381113, -8.443147612205713)], [(9.941974207381113, -8.443147612205713), (-49.00005383187724, 26.67903709411621)], [(-49.00005383187724, 26.67903709411621), (-27.6707141672337, 35.62775793363707)], [(-27.6707141672337, 35.62775793363707), (-25.370136981232626, 36.59296417236328)], [(-25.370136981232626, 36.59296417236328), (-17.67048058274724, 32.004918206981515)], [(-17.67048058274724, 32.004918206981515), (-17.67047789372121, 39.823354759336716)], [(-17.67047789372121, 39.823354759336716), (-15.389519570968819, 40.78033047985461)], [(-15.389519570968819, 40.78033047985461), (-10.952136596378454, 42.6420283597375)], [(-10.952136596378454, 42.6420283597375), (-10.824271210784474, 42.695673228930765)], [(-10.824271210784474, 42.695673228930765), (-10.086395390232557, 41.46301557674714)], [(-10.086395390232557, 41.46301557674714), (-10.002509724424234, 41.35431555342134)], [(-10.002509724424234, 41.35431555342134), (-8.704950563036096, 39.67292163219869)], [(-8.704950563036096, 39.67292163219869), (-8.476342901828819, 39.445889811050975)], [(-8.476342901828819, 39.445889811050975), (-7.205997278768589, 38.18430393042397)], [(-7.205997278768589, 38.18430393042397), (-6.844266383004934, 37.92210342798714)], [(-6.844266383004934, 37.92210342798714), (-5.647135457489535, 37.054360789911506)], [(-5.647135457489535, 37.054360789911506), (-5.185521079083278, 36.83883105722114)], [(-5.185521079083278, 36.83883105722114), (-4.088275161433622, 36.32652223325617)], [(-4.088275161433622, 36.32652223325617), (-3.5747567368640736, 36.224512330345604)], [(-3.5747567368640736, 36.224512330345604), (-2.589320665449436, 36.028757687985944)], [(-2.589320665449436, 36.028757687985944), (-2.0777217218750934, 36.08199440457676)], [(-2.0777217218750934, 36.08199440457676), (-1.2078764994314763, 36.17251004024554)], [(-1.2078764994314763, 36.17251004024554), (-0.7486754672781037, 36.39237102639712)], [(-0.7486754672781037, 36.39237102639712), (0.002969911687202398, 36.75225152030767)], [(0.002969911687202398, 36.75225152030767), (0.3705991468636425, 37.11978489151031)], [(0.3705991468636425, 37.11978489151031), (0.9966843116151471, 37.745708023302456)], [(0.9966843116151471, 37.745708023302456), (1.2505162551949347, 38.21631182856846)], [(1.2505162551949347, 38.21631182856846), (1.7350829040605342, 39.11469461670211)], [(1.7350829040605342, 39.11469461670211), (1.8725761368218432, 39.626296679657216)], [(1.8725761368218432, 39.626296679657216), (2.1897854854574437, 40.806610406600996)], [(2.1897854854574437, 40.806610406600996), (2.227837641822302, 41.28984933386557)], [(2.227837641822302, 41.28984933386557), (2.343321755699292, 42.756426385923334)], [(2.343321755699292, 42.756426385923334), (2.3153259618521194, 43.14531698130738)], [(2.3153259618521194, 43.14531698130738), (2.1897842113595507, 44.88922202508383)], [(2.1897842113595507, 44.88922202508383), (2.14058984744665, 45.13089901762892)], [(2.14058984744665, 45.13089901762892), (1.7350836354974737, 47.12302992355058)], [(1.7350836354974737, 47.12302992355058), (1.7145841753778255, 47.185466229818)], [(1.7145841753778255, 47.185466229818), (1.492126733352659, 47.86301554919434)], [(1.492126733352659, 47.86301554919434), (1.5881124186111115, 47.90328746413284)], [(1.5881124186111115, 47.90328746413284), (1.6164210595992459, 47.915163503231376)], [(1.6164210595992459, 47.915163503231376), (2.8786696441184967, 48.44473916721805)]]
# seg = [[(-15.563175608787557, -10.716349262225991),  (-3.201543941792461, 9.023806543267353)], [(-15.563175692866835, -10.716349644005245), (-3.2015438577131956, 9.023806161488103)]]
# gr1 = GeomGraph()
# gr1.add_s(*seg[0])
# gr1.add_s(*seg[1])
a = 1
# a, b = gr1.partition()
"""
a = gr1.segments
draw_graph(gr1.segments, [], 0, 5, 0, 4)  #
ver = gr1.vertices
arc = gr1.edges
gr2 = gr1.make_pslg()
t1 = gr2.has_segment((1, 1), (3, 3))
t2 = gr2.has_segment((2, 2), (1, 1))
gr2.add_p((3.25, 2))
c = gr2.add_s((3.25, 2), (3.25, 1.5))
m = gr2.add_s((3.25, 2), (3.25, 1.5))
gr2.rem_s((2.75, 1.5), (3.25, 1.5))
b = gr2.segments
# draw_graph(gr2.segments, [])

gr3 = gr2.clipping()  # добавить параметр и проверить add и rem в geomgraph
draw_graph(gr2.segments, [])
draw_graph(gr3.segments, [])
# new_dcel_comps = gr2.get_comps()  # из них достаём контура, возможно без компонент
graph2 = DCEL(gr2)
new_comps = gr3.get_comps()
ans = new_comps[0].partition()
ans2 = new_comps[1].partition()
a = 1
"""
