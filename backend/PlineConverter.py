from base.geom.primitives.dcel import DCEL
from base.geom.primitives.geomgraph import GeomGraph
from base.geom.primitives.linear import PLine, Contour, Polygon
from copy import deepcopy


def convertGGtoPointLines(graph):
    g = deepcopy(graph)
    clip_parts = g.clipping()
    if not g.is_empty():
        dcel = DCEL(g)
        lines = dcel.get_all_contours(external_only=True)
    else:
        lines = []
    new_comps = clip_parts.get_comps()
    for part in new_comps:
        gr_list, pline_list = part.partition()
        for pline in pline_list:
            lines.append(pline.points())
    return lines


class PlainConverter:
    def do(self, primitive):
        if isinstance(primitive, PLine):
            return [primitive.points()]
        if isinstance(primitive, Contour):
            return [primitive.points()]
        if isinstance(primitive, Polygon):
            # хотим вернуть набор линий
            p_lines = [primitive.contour.points()]
            for cont in primitive.holes:
                p_lines.append(cont.points())
            return p_lines
        if isinstance(primitive, DCEL):
            # gg_primitive = primitive.convert_to_gg()
            # p_lines = convertGGtoPointLines(gg_primitive)
            return primitive.get_all_contours(external_only=True)
        if isinstance(primitive, GeomGraph):
            p_lines = convertGGtoPointLines(primitive)
            return p_lines
        return None


