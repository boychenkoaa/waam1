from collections import namedtuple
Message = namedtuple('Message', ['type', 'data'])


class iMediator:
    def __init__(self, *mediator_clients):
        for mediator_client in mediator_clients:
            mediator_client.mediator = self


class SmartMediator(iMediator):
    __slots__ = ["_point_id_container", "_collision_detector"]

    def __init__(self, point_id_container, collision_detector) -> None:
        super().__init__(point_id_container, collision_detector)
        self._point_id_container = point_id_container
        self._collision_detector = collision_detector

    # all func from point_id_container to collision_detector
    def add_point(self, point_data):
        self._collision_detector.insert(point_data)

    def remove(self, point_value):
        self._collision_detector.remove(point_value)


class SoftwarePartsMediator(iMediator):
    __slots__ = ["_backend", "_gui"]

    def __init__(self, backend, gui) -> None:
        super().__init__(backend, gui)
        self._backend = backend
        self._gui = gui

    def msg_for_gui(self, msg_data):
        self._gui.display(msg_data)

    def add(self, msg_data):
        self._backend.add(msg_data)

    def add_buffer(self, ids, dist):
        self._backend.add_buffer(ids, dist)


class StorageMediator(iMediator):
    __slots__ = ["_storage", "_group_container"]

    def __init__(self, storage, group_container) -> None:
        super().__init__(storage, group_container)
        self._storage = storage
        self._group_container = group_container

    def remove_from_all(self, msg_data):
        self._group_container.rem_id_from_all_groups(msg_data, True)


class BaseMediatorClient:
    # iMediator: SmartMediator, SoftwarePartsMediator или StorageMediator
    def __init__(self, mediator=None) -> None:
        self._mediator = mediator

    @property
    def mediator(self):
        return self._mediator

    @mediator.setter
    def mediator(self, mediator):
        self._mediator = mediator
