from copy import deepcopy

from base.geom.algo.bentley import bentli_ottman
from base.geom.primitives.geomgraph import GeomGraph
from base.geom.raw.raw import distance_pp, EPSILON


# обертки над методами самого класса


# учитывать
def planarize(gg: GeomGraph, keep_isolated_points=False):
    arc_list = gg.segments
    if arc_list is not []:
        crossing_edges, crossing_points = bentli_ottman(arc_list)
        new_crossing_edges = list(filter(lambda seg: distance_pp(seg[0], seg[1]) > EPSILON, crossing_edges))
        if keep_isolated_points:
            new_graph = GeomGraph(new_crossing_edges, crossing_points)
        else:
            new_graph = GeomGraph(new_crossing_edges)
        return new_graph