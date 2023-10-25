BEGIN, END = 0, 1
from sortedcontainers.sortedlist import SortedKeyList
from copy import copy, deepcopy

# o -- output
# i -- input
# v -- vertices / vertex
# a -- arc/arcs
# l -- list


class iGraph:
    def has_v(self, vertex):
        pass

    def add_v(self, vertex):
        pass

    def rem_v(self, vertex):
        pass

    def vertices(self):
        pass


class DiGraph(iGraph):
    __slots__ = ["_input_al", "_output_al", "_vertices"]

    def __init__(self):
        self._input_al = dict()
        self._output_al = dict()
        self._vertices = set()

    def __contains__(self, vertex):
        return vertex in self._vertices

    @property
    def vertices(self):
        return copy(self._vertices)

    @property
    def arcs(self):
        return [(begin, end) for begin in self._output_al.keys() for end in self._output_al[begin]]

    def get_iv(self, vertex):
        assert self.has_v(vertex)
        return copy(self._input_al[vertex])

    def get_ov(self, vertex):
        assert self.has_v(vertex)
        return copy(self._output_al[vertex])

    def get_ia(self, vertex):
        assert self.has_v(vertex)
        return [(begin, vertex) for begin in self._input_al[vertex]]

    def get_oa(self, vertex):
        assert self.has_v(vertex)
        return [(vertex, end) for end in self._output_al[vertex]]

    def rem_a(self, arc):
        assert self.has_a(arc)
        self._output_al[arc[0]].remove(arc[1])
        self._input_al[arc[1]].remove(arc[0])

    def rem_v(self, vertex):
        assert self.has_v(vertex)
        for arc in self.get_ia(vertex)+self.get_oa(vertex):
            self.rem_a(arc)

        self._output_al.pop(vertex)
        self._input_al.pop(vertex)
        self._vertices.remove(vertex)

    def has_v(self, vertex):
        return vertex in self._vertices

    def has_a(self, arc):
        if not (self.has_v(arc[0]) and self.has_v(arc[1])):
            return False

        return (arc[0] in self._input_al[arc[1]]) and (arc[1] in self._output_al[arc[0]])

    def add_v(self, vertex):
        assert not self.has_v(vertex)
        self._output_al[vertex] = set()
        self._input_al[vertex] = set()
        self._vertices.add(vertex)

    def add_a(self, arc):
        # if arc[0] == arc[1]:
            # print(arc[0], arc[1])
        assert arc[0] != arc[1]
        assert not self.has_a(arc)
        if arc[0] not in self:
            self.add_v(arc[0])
        if arc[1] not in self:
            self.add_v(arc[1])
        self._output_al[arc[0]].add(arc[1])
        self._input_al[arc[1]].add(arc[0])

    def __getitem__(self, item):
        return list(self._vertices)[item]

    def __repr__(self):
        return "DiGraph\n" + "Vertices: " + str(self._vertices) + "\nArcs: " + str(self.arcs)

    def deg_ov(self, vertex):
        return len(self._output_al[vertex])

    def deg_iv(self, vertex):
        return len(self._input_al[vertex])


class qIsolatedVerticesDi:
    __slots__ = ["_graph"]

    def __init__(self, graph: DiGraph):
        self._graph = graph

    def do(self):
        ans = []
        for v in self._graph.vertices:
            if self._graph.deg_iv(v) + self._graph.deg_ov(v):
                ans.append(v)
        return ans


class Graph(iGraph):
    __slots__ = ["_digraph"]

    def __init__(self):
        self._digraph = DiGraph()

    def make_graph(self, vert_list, edge_list):
        for vert in vert_list:
            self._digraph.add_v(vert)
        for edge in edge_list:
            self._digraph.add_a(edge)
            self._digraph.add_a(edge[::-1])

    def make_graph_from_adjacency_list(self, adjacency_list):
        for key, val in adjacency_list.items():
            if not val in self:
                self._digraph.add_v(val)
            if not key in self:
                self._digraph.add_v(key)
            self._digraph.add_a([key, val])
            self._digraph.add_a([val, key])

    # переделать, хотим получить и рёбра
    def iter_dfs(self, node, edges):  # node - вершина начала поиска
        S, Q = set(), []
        Q.append(node)
        while Q:
            u = Q.pop()
            if u in S:
                continue
            S.add(u)
            a = self[u]
            for ai in a:
                edges.append([u, ai])
            Q.extend(a)  # вершины, которые могут быть достигнуты из u
            yield u

    def get_connectivity_components(self):
        # возвращает словарь {номер вершины: номер компоненты связности}
        comp = []
        node_list = list(self._digraph.vertices)
        while len(node_list) > 0:
            node = node_list[0]
            edges = []
            tree = list(self.iter_dfs(node, edges))
            comp.append((tree, edges))
            list(map(lambda x: node_list.remove(x), tree))
        # запускать рекурсивно из вершин: исходные - посещённые на предыдущем шаг
        return comp

    def add_v(self, vertex):
        self._digraph.add_v(vertex)

    def add_e(self, edge):
        self._digraph.add_a(edge)
        self._digraph.add_a(edge[::-1])

    @property
    def edges(self):
        return list(filter(lambda x: x[0] <= x[1], self._digraph.arcs))

    @property
    def arcs(self):
        return list(self._digraph.arcs)

    @property
    def vertices(self):
        return self._digraph.vertices

    def adj_list(self, vertex: int):
        return self._digraph.get_ov(vertex)

    def has_e(self, edge):
        return self._digraph.has_a(edge)

    def has_v(self, vertex):
        return self._digraph.has_v(vertex)

    def __getitem__(self, vertex):
        return self.adj_list(vertex)

    def deg_v(self, vertex):
        return len(self[vertex])

    def __contains__(self, item):
        return item in self._digraph

    def get_ev(self, vertex):
        return [(vertex, end) for end in self[vertex]]

    def rem_v(self, vertex):
        self._digraph.rem_v(vertex)

    def rem_e(self, edge):
        self._digraph.rem_a(edge)
        self._digraph.rem_a(edge[::-1])

    def get_isolated_v(self):
        output_vertex = []
        for vert in self.vertices:
            if self.deg_v(vert) == 0:
                output_vertex.append(vert)
        return output_vertex

    def del_isolated_v(self):
        for vert in self.vertices:
            if self.deg_v(vert) == 0:
                self.rem_v(vert)

    def get_pendant_v(self):
        output_vertex = []
        for vert in self.vertices:
            if self.deg_v(vert) == 1:
                output_vertex.append(vert)
        return output_vertex

    def is_empty(self):
        return not (self.get_isolated_v()) and not (self.edges)


class qIsolatedVertices:
    __slots__ = ["_graph"]

    def __init__(self, graph: Graph):
        self._graph = graph

    def do(self):
        ans = []
        for v in self._graph.vertices:
            if self._graph.deg_v(v) == 0:
                ans.append(v)
        return ans


class BiGraph(iGraph):
    __slots__ = ["_red_vert", "_blue_vert", "_red_connections", "_blue_connections"]

    def __init__(self):
        self._red_connections = dict()
        self._blue_connections = dict()
        self._red_vert = set()
        self._blue_vert = set()

    def has_red_v(self, vertex):
        return vertex in self._red_vert

    def has_blue_v(self, vertex):
        return vertex in self._blue_vert

    def add_red_v(self, vertex):
        assert not self.has_red_v(vertex)
        self._red_connections[vertex] = set()
        self._red_vert.add(vertex)

    def add_red_vertices(self, vertices):
        for vert in vertices:
            self.add_red_v(vert)

    def add_blue_v(self, vertex):
        assert not self.has_blue_v(vertex)
        self._blue_connections[vertex] = set()
        self._blue_vert.add(vertex)

    def add_blue_vertices(self, vertices):
        for vert in vertices:
            if not self.has_blue_v(vert):
                self.add_blue_v(vert)

    def is_bipartite_vertices(self, red_v, blue_v):
        return self.has_red_v(red_v) and self.has_blue_v(blue_v)

    def has_red_blue_e(self, edge):
        assert self.is_bipartite_vertices(edge[0], edge[1])
        return (edge[1] in self._red_connections[edge[0]]) and (edge[0] in self._blue_connections[edge[1]])

    def has_blue_red_e(self, edge):
        assert self.is_bipartite_vertices(edge[1], edge[0])
        return (edge[1] in self._blue_connections[edge[0]]) and (edge[0] in self._red_connections[edge[1]])

    def add_red_blue_e(self, edge):
        # предполагается, что вершины уже добавлены в граф, но связи между ними нет
        assert not self.has_red_blue_e(edge)
        if self.has_red_v(edge[0]):
            self._red_connections[edge[0]].add(edge[1])
            self._blue_connections[edge[1]].add(edge[0])

    def rem_red_blue_e(self, edge):
        assert self.has_red_blue_e(edge)
        self._red_connections[edge[0]].remove(edge[1])
        self._blue_connections[edge[1]].remove(edge[0])

    def add_rb_edges(self, edge_list):
        for edge in edge_list:
            self.add_red_blue_e(edge)

    def rem_red_v(self, vertex):  # тут проверить !!
        assert self.has_red_v(vertex)
        for bl_vt in self._red_connections[vertex]:
            self._blue_connections[bl_vt].remove(vertex)
        self._red_connections.pop(vertex)
        self._red_vert.remove(vertex)

    def rem_blue_v(self, vertex):  # тут проверить !!
        assert self.has_blue_v(vertex)
        for rd_vt in self._blue_connections[vertex]:
            self._red_connections[rd_vt].remove(vertex)
        self._blue_connections.pop(vertex)
        self._blue_vert.remove(vertex)

    def deg_red_vert(self, vert):
        assert self.has_red_v(vert)
        return len(self._red_connections[vert])

    def deg_blue_vert(self, vert):
        assert self.has_blue_v(vert)
        return len(self._blue_connections[vert])

    def get_adj_list_red(self, vertex: int):
        assert self.has_red_v(vertex)
        return self._red_connections[vertex]

    def get_adj_list_blue(self, vertex: int):
        assert self.has_blue_v(vertex)
        return self._blue_connections[vertex]

    @property
    def edges(self):
        edge_list = []
        for r_vert in self._red_vert:
            for b_vert in self._red_connections[r_vert]:
                edge_list.append([r_vert, b_vert])
        return edge_list

    @property
    def red_vertices(self):
        return list(self._red_vert)

    @property
    def blue_vertices(self):
        return list(self._blue_vert)

    # геттеры!!


"""
gr1 = Graph()
gr1.add_v(1)
gr1.add_v(2)
gr1.add_e((1, 2))
gr1.add_v(3)
gr1.add_e((1, 3))
gr1.add_e((2, 3))
ver = gr1.vertices
a = gr1.adj_list(1)
ans = {3: 0, 5: 3, 6: 0}
gr2 = DiGraph()
gr2.make_graph(ans)
a = gr2.components(ans)

arc = gr2.arcs  # протестировать
# print(ver)
print(arc)


b_gr = BiGraph()
b_gr.add_red_vertices([1, 3, 5, 7])
b_gr.add_blue_vertices([1, 2, 4, 6, 8])
b_gr.add_rb_edges([(1, 2), (1, 4), (3, 4), (3, 8), (7, 8), (1, 1), (7, 1)])
ed = b_gr.edges
adj = b_gr.get_adj_list_blue(1)
b_gr.rem_blue_v(4)
a = 1
"""