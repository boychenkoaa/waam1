from copy import deepcopy


class IDEntity:
    __slots__ = ["_id", "_value"]

    def __init__(self, id_, value=None):
        self._id = id_
        self._value = value

    def set_value(self, new_value):
        self._value = deepcopy(new_value)

    @property
    def value(self):
        return self._value

    @property
    def id(self):
        return self._id

