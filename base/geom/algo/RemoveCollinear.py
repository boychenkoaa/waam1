from base.geom.primitives.geomgraph import GeomGraph
from base.geom.raw.raw import orient_determinant, EPSILON
from copy import deepcopy, copy
from base.geom.primitives.dcel import DCEL


# потенциально может быть квадратичным
# всех кто на удаление - составляем список и двигаем два индикатора
# дергаем список точек, ищем точки под удаление и двумя индексами за линейное время удаляем


def remove_collinear(old_prim):
    prim = deepcopy(old_prim)
    if prim.type in ["PLine", "Contour"]:
        for i in prim.raw:
            if abs(orient_determinant(prim[i-3], prim[i-2], prim[i-1])) < EPSILON:
                prim.pop(i-2)
    elif prim.type == "Polygon":
        for j in prim.raw[0]:
            if abs(orient_determinant(prim[(j[0], j[1] - 3)], prim[(j[0], j[1] - 2)],
                                      prim[(j[0], j[1] - 1)])) < EPSILON:
                prim.pop((j[0], j[1] - 2))
        for i in prim.raw[1]:
            for j in i:
                if abs(orient_determinant(prim[(j[0], j[1] - 3)], prim[(j[0], j[1] - 2)],
                                          prim[(j[0], j[1] - 1)])) < EPSILON:
                    prim.pop((j[0], j[1] - 2))
    elif prim.type == "GeomGraph":
        vertices = prim.vertices
        for vert in vertices:
            if prim.deg(vert) == 2:
                neigh = copy(prim.get_neigh(vert))
                n1 = neigh.pop()
                n2 = neigh.pop()
                if abs(orient_determinant(prim[n1], prim[n2], prim[vert])) < EPSILON:
                    prim.rem_id(vert)
                    prim.add_e([n1, n2])
    elif prim.type == "DCEL":
        prim = prim.convert_to_gg()
        vertices = prim.vertices
        for vert in vertices:
            if prim.deg(vert) == 2:
                neigh = copy(prim.get_neigh(vert))
                n1 = neigh.pop()
                n2 = neigh.pop()
                if abs(orient_determinant(prim[n1], prim[n2], prim[vert])) < EPSILON:
                    prim.rem_id(vert)
                    prim.add_e([n1, n2])
    return DCEL(prim)
