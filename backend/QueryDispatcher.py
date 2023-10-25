from backend.Queries import qGetAll, qGetType, qGetData, qGetDP, qGetIDlist, qCopy, qRotation, qAddBuffer, qRaster, \
    qAddSlice, qGetSliceData, qGetAllSlices  # qGetObjByGroups
from backend.Specifications import get_type_spec, get_data_spec, get_slice_data_spec, \
    get_dp_spec, get_copy_spec, get_equidistant_spec, get_raster_spec, get_rotation_spec, get_add_slice_spec, \
    get_move_spec


class QueryDispatcher:
    __slots__ = ["_storage"]

    def __init__(self, storage):
        self._storage = storage

    def create_from(self, info: dict):
        creation_type = info["type"]
        if creation_type == "get all":
            return self.create_get_all()
        if creation_type == "get all slice ids":
            return self.create_get_all_slice_ids()
        if creation_type == "get type":
            return self.create_get_type(info["params"])
        if creation_type == "get data":
            return self.create_get_data(info["params"])
        if creation_type == "get data by slice":
            return self.create_get_data_by_slice(info["params"])
        if creation_type == "get dp":
            return self.create_get_dp(info["params"])
        if creation_type == "get ids":
            return self.create_get_ids()
        if creation_type in ["get copy", "get move"]:
            return self.create_get_copy(info["params"])
        if creation_type == "get rotation":
            return self.create_get_rotation(info["params"])
        if creation_type == "get equidistant":
            return self.create_get_equidistant(info["params"])
        if creation_type == "get raster":
            return self.create_get_raster(info["params"])
        if creation_type == "get slice":
            return self.create_get_slice(info["params"])

    def create_get_all(self):
        return qGetAll(self._storage)

    def create_get_all_slice_ids(self):
        return qGetAllSlices(self._storage)

    def create_get_type(self, params):
        b_id = params["geom_id"]
        return qGetType(self._storage, b_id) if get_type_spec.validate(params) else None

    def create_get_data(self, params):
        b_id = params["geom_id"]
        return qGetData(self._storage, b_id) if get_data_spec.validate(params) else None

    def create_get_data_by_slice(self, params):
        s_id = params["slice_id"]
        return qGetSliceData(self._storage, s_id) if get_slice_data_spec.validate(params) else None

    def create_get_ids(self):
        return qGetIDlist(self._storage)

    def create_get_dp(self, params):  # достать из слоя - ?
        b_id = params["geom_id"]
        return qGetDP(self._storage, b_id) if get_dp_spec.validate(params) else None

    def create_get_copy(self, params):
        b_id_list = params["id_list"]
        vec = params["displacement_vector"]
        return qCopy(self._storage, b_id_list, vec) if get_copy_spec.validate(params) else None

    def create_get_move(self, params):
        b_id_list = params["id_list"]
        vec = params["displacement_vector"]
        return qCopy(self._storage, b_id_list, vec) if get_move_spec.validate(params) else None

    def create_get_rotation(self, params):
        b_id_list = params["id_list"]
        center = params["rotation_center"]
        angle = params["rotation_angle"]
        return qRotation(self._storage, b_id_list, center, angle) \
            if get_rotation_spec.validate(params) else None

    def create_get_equidistant(self, params):
        b_id = params["poly_id"]
        dist_list = params["distance_list"]
        buffer_type = params["without_shrink"]
        work_with_hole_type = params["cut_holes"]
        return qAddBuffer(self._storage, b_id, dist_list, buffer_type, work_with_hole_type) \
            if get_equidistant_spec.validate(params) else None

    def create_get_raster(self, params):
        b_id = params["poly_id"]
        slope_k = params["slope"]
        bead_width = params["bead_width"]
        initial_indent = params["initial_indent"]
        line_count = params["line_count"]
        return qRaster(self._storage, b_id, slope_k, bead_width, initial_indent, line_count) \
            if get_raster_spec.validate(params) else None

    def create_get_slice(self, params):
        segment_list = params["segment_list"]
        return qAddSlice(self._storage, segment_list) if get_add_slice_spec.validate(params) else None
