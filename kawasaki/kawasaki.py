from collections import namedtuple
from copy import copy, deepcopy

OAT = namedtuple("OAT", ["o", "a", "t"])
XYZ = namedtuple("XYZ", ["x", "y", "z"])
XYZOAT = namedtuple("XYZOAT", ["x", "y", "z", "o", "a", "t"])

class ipathImporter:
    def __init__(self):
        self.path = []
        pass

    def imp(self, filename: str):
        pass

class txt_XYZ_pathImporter(ipathImporter):
    def __init__(self):
        super().__init__()

    def imp(self, filename: str):
        f = open(filename)
        assert f
        path = [XYZOAT(*(list(map(float, line.split()))), 0, 0, 0) for line in f]
        f.close()
        return path

class txt_XYZOAT_pathImporter(ipathImporter):
    def __init__(self):
        super().__init__()

    def imp(self, filename: str):
        f = open(filename)
        assert f
        path = [XYZOAT(*(map(float, line.split()))) for line in f]
        f.close()
        return path


class ikwpath:
    def __init__(self):
        self.p = []
        pass

    def __repr__(self):
        return sum(map(lambda point: str(point) + "\n", self.p))

    def export(self):
        pass

    def append(self, point):
        self.p.append(point)

    def insert(self, index, point):
        self.p.insert(index, point)

    def pop(self, index):
        return self.p.pop(index)


class xyzkwpath(ikwpath):
    def __init__(self, o: float, a: float, t: float):
        super().__init__()
        self.__oat = OAT(o, a, t)

    def set_oat(self, o: float, a: float, t: float):
        self.__oat = OAT(o, a, t)



move_params = namedtuple("move_params", ["accurancy", "free_speed"])
weld_params = namedtuple("weld_params", ["speed"])



