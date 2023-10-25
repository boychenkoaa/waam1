from backend.Specifications import add_pline_spec, add_poly_spec, add_slice_spec, add_empty_slice_spec, remove_spec, \
    change_active_slice_spec, remove_slice_spec, change_slice_description_spec, replace_to_another_slice_spec, \
    move_spec, copy_spec, rotate_spec, pline_cut_poly_spec, cut_spec, move_point_spec, move_point_poly_spec, \
    move_point_gg_spec, add_to_group_spec, group_disband_spec, new_group_spec, raster_spec, \
    convert_poly_to_contours_spec, convert_contours_to_poly_spec, revers_spec, equidistant_spec, remove_collinear_spec, \
    move_point_dcel_spec, add_point_spec, add_point_to_poly_spec, add_point_to_nonlinear_spec, remove_point_spec, \
    remove_point_from_poly_spec, remove_point_from_nonlinear_spec
from backend.commands.RepoCommands import Add, \
    Remove, AddSlice, AddEmptySlice, RemoveSlice, ChangeActiveSlice, \
    ChangeSliceDescription, ReplaceToAnotherSlice, AddPolygon
from backend.commands.AplayAlgoCommands import Copy, ConvertContoursToPoly, \
    MovePointDCEL, ConvertPolyToContours, RemoveCollinear, \
    AddRaster, Cut, CreateGroup, DisbandGroup, \
    AddObjectsToGroup, Equidistant, AddPointToEdgeCenterGraph, RemPointFromGraph, CutPolyWithPline
from backend.commands.EditCommands import Move, Rotation, Revers, AddPointToEdgeCenter, AddPointToPolyEdgeCenter, \
    RemPoint, RemPointFromPoly, MovePoint, MovePointFromPoly, MovePointGG


# AddPointToEdgeCenterGG, AddPointToEdgeCenterDCEL, RemPointFromGG, RemPointFromDCEL, MovePointGG, MovePointDCEL


class CommandDispatcher:
    __slots__ = ["_storage"]

    def __init__(self, storage):
        self._storage = storage

    def create_from(self, info: dict):
        creation_type = info["type"]
        if creation_type == "add":  # 1
            return self.create_add_primitive(info["params"])
        if creation_type == "add polygon":  # 1
            return self.create_add_polygon(info["params"])
        if creation_type == "add slice":  # 1
            return self.create_add_slice(info["params"])
        if creation_type == "add empty slice":  # 1
            return self.create_add_empty_slice(info["params"])
        if creation_type == "remove":  # list
            return self.create_remove(info["params"])
        if creation_type == "remove slice":  # 1
            return self.create_remove_slice(info["params"])
        if creation_type == "change active slice":  # 1
            return self.create_change_active_slice(info["params"])
        if creation_type == "change slice description":  # 1
            return self.create_change_slice_description(info["params"])
        if creation_type == "replace to another slice":  # list
            return self.create_replace_to_another_slice(info["params"])
        if creation_type == "move":  # list
            return self.create_move(info["params"])
        if creation_type == "copy":  # list
            return self.create_copy(info["params"])
        if creation_type == "rotate":  # list
            return self.create_rotate(info["params"])
        if creation_type == "pline cut polygon":  # 1 доделать!
            return self.create_cut_polygon(info["params"])
        if creation_type == "cut":   # 1 точечный
            return self.create_cut(info["params"])
        if creation_type == "add point":  # 1
            return self.create_add_point(info["params"])
        if creation_type == "add point to poly":  # 1
            return self.create_add_point_to_poly(info["params"])
        if creation_type == "add point to nonlinear":  # 1
            return self.create_add_point_to_nonlinear(info["params"])
        if creation_type == "remove point":  # 1
            return self.create_rem_point(info["params"])
        if creation_type == "remove point rom poly":  # 1
            return self.create_rem_point_from_poly(info["params"])
        if creation_type == "remove point rom nonlinear":  # 1
            return self.create_rem_point_from_nonlinear(info["params"])
        if creation_type == "move point":  # 1
            return self.create_move_point(info["params"])
        if creation_type == "move point poly":  # 1
            return self.create_move_point_poly(info["params"])
        if creation_type == "move point gg":  # 1
            return self.create_move_point_gg(info["params"])
        if creation_type == "move point dcel":  # 1
            return self.create_move_point_dcel(info["params"])
        if creation_type == "remove collinear":  # 1 - пока что
            return self.create_remove_collinear(info["params"])
        if creation_type == "equidistant":  # 1
            return self.create_get_equidistant(info["params"])
        if creation_type == "revers":  # list
            return self.create_revers(info["params"])
        if creation_type == "convert poly to contours":  # 1
            return self.create_convert_poly_to_contours(info["params"])
        if creation_type == "convert contours to poly":  # list
            return self.create_convert_contours_to_poly(info["params"])
        if creation_type == "raster":  # 1
            return self.create_get_raster(info["params"])
        if creation_type == "new group":  # 1
            return self.create_new_group(info["params"])
        if creation_type == "disband group":  # 1
            return self.create_group_disband(info["params"])
        if creation_type == "add objects to group":
            return self.create_add_to_group(info["params"])

    def create_add_primitive(self, params):
        points = params["point_list"]
        return Add(self._storage, points) if add_pline_spec.validate(params) else None  # придумать ответ

    def create_add_polygon(self, params):
        contour = params["point_list"]
        holes = params["list_of_point_list"]
        return AddPolygon(self._storage, contour, holes) if add_poly_spec.validate(params) else None

    def create_add_slice(self, params):
        segment_list = params["segment_list"]
        return AddSlice(self._storage, segment_list) if add_slice_spec.validate(params) else None

    def create_add_empty_slice(self, params):
        cs = params["coordinate_system"]
        description = params["description"]
        return AddEmptySlice(self._storage, cs, description) if add_empty_slice_spec.validate(params) else None

    def create_remove(self, params):
        id_list = params["id_list"]
        return Remove(self._storage, id_list) if remove_spec.validate(params) else None

    def create_change_active_slice(self, params):
        new_active_id = params["slice_id"]
        return ChangeActiveSlice(self._storage, new_active_id) \
            if change_active_slice_spec.validate(params) else None

    def create_remove_slice(self, params):
        slice_id = params["slice_id"]
        return RemoveSlice(self._storage, slice_id) if remove_slice_spec.validate(params) else None

    def create_change_slice_description(self, params):
        slice_id = params["slice_id"]
        new_descript = params["description"]
        return ChangeSliceDescription(self._storage, slice_id, new_descript) \
            if change_slice_description_spec.validate(params) else None

    def create_replace_to_another_slice(self, params):
        old_slice_id = params["slice_id"]
        new_slice_id = params["new_slice_id"]  # использование дублей параметра, или сделать параметр из двух id слайсов
        id_list = params["id_list"]
        return ReplaceToAnotherSlice(self._storage, old_slice_id, new_slice_id, id_list) \
            if replace_to_another_slice_spec.validate(params) else None

    def create_move(self, params):
        id_list = params["id_list"]
        vec = params["displacement_vector"]
        return Move(self._storage, id_list, vec) if move_spec.validate(params) else None

    def create_copy(self, params):
        id_list = params["id_list"]
        vec = params["displacement_vector"]
        return Copy(self._storage, id_list, vec) if copy_spec.validate(params) else None

    def create_rotate(self, params):
        id_list = params["id_list"]
        angle = params["rotation_angle"]
        center = params["rotation_center"]
        return Rotation(self._storage, id_list, center, angle) \
            if rotate_spec.validate(params) else None

    def create_cut_polygon(self, params):
        pline_id = params["pline_id"]
        polygon_id = params["poly_id"]
        return CutPolyWithPline(self._storage, pline_id, polygon_id) \
            if pline_cut_poly_spec.validate(params) else None

    def create_cut(self, params):
        geom_obj_id = params["geom_id"]
        coord_for_cut = params["user_coord"]
        cut_area = params["area"]
        at_existed_points = params["only_from_existing"]
        return Cut(self._storage, geom_obj_id, True, coord_for_cut, cut_area, at_existed_points) \
            if cut_spec.validate(params) else None

    def create_add_point(self, params):
        geom_id = params["geom_id"]
        id_ = params["prev_ind"]
        return AddPointToEdgeCenter(self._storage, geom_id, id_) \
            if add_point_spec.validate(params) else None

    def create_add_point_to_poly(self, params):
        geom_id = params["poly_id"]
        id_ = params["polygon_prev_ind"]
        return AddPointToPolyEdgeCenter(self._storage, geom_id, id_) \
            if add_point_to_poly_spec.validate(params) else None

    def create_add_point_to_nonlinear(self, params):
        geom_id = params["geom_id"]
        id1 = params["prev_ind"]
        id2 = params["post_ind"]
        return AddPointToEdgeCenterGraph(self._storage, geom_id, id1, id2) \
            if add_point_to_nonlinear_spec.validate(params) else None

    def create_rem_point(self, params):
        geom_id = params["geom_id"]
        point_id = params["point_ind"]
        return RemPoint(self._storage, geom_id, point_id) \
            if remove_point_spec.validate(params) else None

    def create_rem_point_from_poly(self, params):
        geom_id = params["geom_id"]
        point_id = params["point_ind"]
        return RemPointFromPoly(self._storage, geom_id, point_id) \
            if remove_point_from_poly_spec.validate(params) else None

    def create_rem_point_from_nonlinear(self, params):
        geom_id = params["poly_id"]
        point_id = params["point_ind"]
        return RemPointFromGraph(self._storage, geom_id, point_id) \
            if remove_point_from_nonlinear_spec.validate(params) else None

    def create_move_point(self, params):
        geom_id = params["geom_id"]
        point_ind = params["point_ind"]
        new_coord = params["new_coord"]
        return MovePoint(self._storage, geom_id, point_ind, new_coord)\
            if move_point_spec.validate(params) else None

    def create_move_point_poly(self, params):
        geom_id = params["poly_id"]
        p_point_ind = params["polygon_point_ind"]
        new_coord = params["new_coord"]
        return MovePointFromPoly(self._storage, geom_id, p_point_ind, new_coord)\
            if move_point_poly_spec.validate(params) else None

    def create_move_point_gg(self, params):
        geom_id = params["gg_id"]
        g_point_ind = params["point_ind"]
        new_coord = params["new_coord"]
        return MovePointGG(self._storage, geom_id, g_point_ind, new_coord)\
            if move_point_gg_spec.validate(params) else None

    def create_move_point_dcel(self, params):
        geom_id = params["dcel_id"]
        d_point_ind = params["point_ind"]
        new_coord = params["new_coord"]
        return MovePointDCEL(self._storage, geom_id, d_point_ind, new_coord)\
            if move_point_dcel_spec.validate(params) else None

    def create_remove_collinear(self, params):  # проверить!
        geom_obj_id = params["geom_id"]
        return RemoveCollinear(self._storage, geom_obj_id, True)\
            if remove_collinear_spec.validate(params) else None  # для любой геометрии

    def create_get_equidistant(self, params):
        geom_id = params["poly_id"]
        dist_list = params["distance_list"]
        cut_holes = params["cut_holes"]  # True/False
        without_shrink = params["without_shrink"]  # True/False
        # add_kwargs = params["add_kwargs"]
        return Equidistant(self._storage, geom_id, dist_list, without_shrink, cut_holes) \
            if equidistant_spec.validate(params) else None

    def create_revers(self, params):  # только для Contour, PLine
        id_list = params["id_list"]
        return Revers(self._storage, id_list) if revers_spec.validate(params) else None

    def create_convert_poly_to_contours(self, params):
        geom_id = params["poly_id"]
        return ConvertPolyToContours(self._storage, geom_id)\
            if convert_contours_to_poly_spec.validate(params) else None

    def create_convert_contours_to_poly(self, params):
        id_list = params["id_list"]
        return ConvertContoursToPoly(self._storage, id_list)\
            if convert_poly_to_contours_spec.validate(params) else None

    def create_get_raster(self, params):
        geom_id = params["poly_id"]
        slope_k = params["slope"]
        bead_width = params["bead_width"]
        initial_indent = params["initial_indent"]
        line_count = params["line_count"]
        return AddRaster(self._storage, geom_id, slope_k, bead_width, initial_indent, line_count) \
            if raster_spec.validate(params) else None

    def create_new_group(self, params):
        id_list = params["id_list"]
        return CreateGroup(self._storage, id_list) if new_group_spec.validate(params) else None

    def create_group_disband(self, params):
        group_id = params["group_id"]
        return DisbandGroup(self._storage, group_id) if group_disband_spec.validate(params) else None

    def create_add_to_group(self, params):
        group_id = params["group_id"]
        id_list = params["id_list"]
        return AddObjectsToGroup(self._storage, group_id, id_list) \
            if add_to_group_spec.validate(params) else None


