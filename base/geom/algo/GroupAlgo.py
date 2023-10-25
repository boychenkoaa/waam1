from base.geom.primitives.group import Group


def create_new_group(geom_obj_id_list):  # слияние нескольких объектов в группу
    return Group(geom_obj_id_list)


def disband_group(group_obj):
    return group_obj.get_primitive_list()


def add_objects_to_list(group_obj, new_geoms):
    old_group_primitives = group_obj.get_primitive_list()
    old_group_primitives.extend(new_geoms)
    return Group(old_group_primitives)

