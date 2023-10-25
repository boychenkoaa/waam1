from copy import copy
from typing import Dict, Union

from points.IDEntity import IDEntity
from sortedcontainers import SortedKeyList

from viewport.viewport2d import viewport2dparameters

X, Y, Z = 0, 1, 2


class CoordinateSystem:
    __slots__ = ["_origin", "shift", "euler_angles"]

    def __init__(self, origin=(0, 0, 0)):
        self._origin = origin

    @property
    def origin(self):
        return self._origin

    def to_wcs3(self, xyz):
        return (xyz[X]+self.origin[X], xyz[Y]+self.origin[Y], xyz[Z]+self.origin[Z])

    def to_wcs2(self, xy):
        return (xy[X]+self.origin[X], xy[Y]+self.origin[Y], self.origin[Z])


WCS = CoordinateSystem((0, 0, 0))
# ddp = dict(color="black", style="solid", width=1)
DPlineP = viewport2dparameters.default_pline_properties
DContP = viewport2dparameters.default_contour_properties
DPolyP = viewport2dparameters.default_polygon_properties
DefaultDP = {"color": "by layer",
             "visible": "by layer",
             "selected": "by layer",
             "style": "by layer",
             "width": "by layer",
             "reverse": "by layer"}


class GeomObject:  # абстрактный класс, сделать наследников с конкретной геометрией
    def __init__(self, geom):  # добавить слайс и лэер
        self.dp_by_layer = False
        self._geom = geom
        """                """
        if self.geom_type == "PLine":
            self._display_prop = DPlineP
        elif self.geom_type == "Contour":
            self._display_prop = DContP
        elif self.geom_type == "Polygon":
            self._display_prop = DPolyP

        # self._display_prop = DefaultDP

    @property
    def geom(self):
        return self._geom

    @property
    def DP(self):
        return copy(self._display_prop)

    @property
    def geom_type(self):
        return self._geom.type

    def set_geom(self, new_geom):
        self._geom = new_geom

    def set_dp(self, prop, new_value):
        self._display_prop[prop] = new_value


class GeomIDEntity(IDEntity):
    __slots__ = ["_id", "_geom_object"]

    def __init__(self, id_: int, geom_object: GeomObject):
        super().__init__(id_, value=geom_object)

    @property
    def geomobject(self):
        return super().value
