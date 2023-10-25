from base.geom.algo.RemoveCollinear import remove_collinear
from base.geom.algo.nearest import nearest
from base.geom.algo.GGalgo import planarize
from base.geom.primitives.geomgraph import GeomGraph
from base.geom.primitives.linear import PLine, Contour
from base.geom.raw.raw import Segment, mov_p_along_s
from base.geom.primitives.dcel import DCEL


def cut_slice(new_gg: GeomGraph):
    new_gg.del_isolated_v()
    clip_parts = new_gg.clipping()  # добавить в отдельные линиии
    new_gg.del_isolated_v()
    new_gg = remove_collinear(new_gg)
    if not new_gg.is_empty():  # хотим получить полигон!!
        new_dcel = DCEL(new_gg)
        poly_list = new_dcel.get_polygons_list()
        if not poly_list:  # send massage to front!!!
            contours = new_dcel.get_all_contours(external_only=False, without_none=True)
            for cont in contours:  # сейчас возвращаем все контура
                poly_list.append(Contour(cont))

    else:
        poly_list = []

    if not clip_parts.is_empty():
        components = clip_parts.get_comps()
        pline_list = []
        for comp in components:
            gr_list, pline_sublist = comp.partition()
            pline_list.extend(pline_sublist)
    else:
        pline_list = []
    return poly_list, pline_list


def cut_poly_with_pline(input_geom_list):
    g_pline = input_geom_list[0]
    # сейчас нам не передаётся id рсдс, найдем его перебором
    new_gg = GeomGraph(input_geom_list[1].segments()) # из полигона сделать гг - ?
    pl_segments = g_pline.segments()
    new_gg.add_segments(pl_segments)
    new_gg = planarize(new_gg)
    if new_gg is not None:
        poly_list, pline_list = cut_slice(new_gg)  # из algo
        poly_list.extend(pline_list)
        return poly_list
    else:
        return g_pline


def cut(prim, user_coord: tuple, area=1, only_from_existing=False):  # prim - contour/pline
    # найдем ближайшую точку к месту клика
    point_loc, dist = nearest(prim, user_coord, area, only_from_existing)
    if point_loc is None:
        return []  # пользователь тыкнул слишком далеко

    # как её добавить?
    prev_ind = point_loc[0]  # id вставки
    d_to_id = point_loc[1]
    point = prim[prev_ind]
    vector = (prim[(prev_ind + 1) % len(prim)][0] - point[0], prim[(prev_ind + 1) % len(prim)][1] - point[1])
    seg = Segment(point, vector)
    new_point = mov_p_along_s(d_to_id, seg)  # точка вставки
    #  достать все точки контура начиная с id + 1 до id, записать в плайн
    if isinstance(prim, PLine):
        first_pline = []
        second_pline = [new_point]
        for ind, id_ in enumerate(prim.raw):
            if ind < prev_ind:
                first_pline.append(prim[ind])
            elif ind == prev_ind:
                first_pline.append(prim[ind])
                first_pline.append(new_point)
            else:
                second_pline.append(prim[ind])

        return [PLine(first_pline), PLine(second_pline)]
    if isinstance(prim, Contour):
        pline = [new_point]
        raw = prim.raw
        for i in range(prev_ind+1, len(raw)):
            pline.append(prim[i])
        for i in range(prev_ind+1):
            # a = pl[i]
            pline.append(prim[i])
        pline.append(new_point)
        return [PLine(pline)]
    return []