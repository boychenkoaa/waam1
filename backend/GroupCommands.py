class cSwap2(iCommand):
    __slots__ = ["__pos1", "__pos2", "__group_name"]

    def __init__(self, storage: Storage, pos1: int, pos2: int, group_name: str):
        super().__init__(storage)
        self.__pos1 = pos1
        self.__pos2 = pos2
        self.__group_name = group_name

    def __validate(self):
        st = [False] * 4
        st[0] = isinstance(self._storage, Storage)
        st[1] = isinstance(self.__group_name, str)
        st[2] = isinstance(self.__pos1, int)
        st[3] = isinstance(self.__pos2, int)
        if not all(st):
            raise TypeError()

    def do(self):
        self._storage.swap2pos(self.__group_name, self.__pos1, self.__pos2)

    def undo(self):
        self._storage.swap2pos(self.__group_name, self.__pos1, self.__pos2)
