from copy import deepcopy

from base.geom.algo.cut import cut_slice
from base.geom.primitives.dcel import DCEL


def move_point_at_dcel(input_dcel, id_, new_point_coord):
    gg_from_dcel = deepcopy(input_dcel).geom.convert_to_gg()
    gg_from_dcel.move_id(id_, new_point_coord)
    new_geom = DCEL(gg_from_dcel)
    return [new_geom]

