from copy import deepcopy
from base.geom.algo.cut import cut_slice
from base.geom.primitives.dcel import DCEL


def add_point_to_graph(input_geom, id1, id2):
    prim = deepcopy(input_geom)
    if prim.type == "GeomGraph":
        return [input_geom.add_p_to_edge_center(id1, id2)]
    elif prim.type == "DCEL":
        gg_from_dcel = deepcopy(input_geom).geom.convert_to_gg()
        gg_from_dcel.add_p_to_edge_center(id1, id2)
        new_geom = DCEL(gg_from_dcel)
        return [new_geom]


def rem_point_from_graph(input_geom, id_):
    prim = deepcopy(input_geom)
    if prim.type == "GeomGraph":
        return [deepcopy(input_geom).rem_id(id_)]
    elif prim.type == "DCEL":
        gg_from_dcel = deepcopy(input_geom).convert_to_gg()
        gg_from_dcel.rem_id(id_)
        if gg_from_dcel.is_empty():  # удаляем объект!
            return []
        elif len(gg_from_dcel.get_isolated_v()) or len(gg_from_dcel.get_pendant_v()):
            new_dcel, pline_list = cut_slice(gg_from_dcel)
            geom_list = [new_dcel]
            geom_list.extend(pline_list)
            return geom_list
        else:
            new_geom = DCEL(gg_from_dcel)
            return [new_geom]

