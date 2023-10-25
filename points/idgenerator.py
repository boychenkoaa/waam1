class iIDGenerator:
    def __init__(self):
        pass

    def new_id(self):
        pass


class SimpleIDGenerator(iIDGenerator):
    def __init__(self):
        super().__init__()
        self.__last_id = -1

    def new_id(self):
        self.__last_id = self.__last_id + 1
        return self.__last_id

