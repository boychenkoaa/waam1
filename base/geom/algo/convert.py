from base.geom.algo.algo import add_slice


# а вот тут никаких списков на входе быть не должно
def convert_poly_to_contours(input_geom_list):
    poly = input_geom_list[0]
    contour_list = poly.get_all_contours()
    return contour_list


def convert_contours_to_poly(input_geom_list):
    # достать все рёбра и повторить add_slice
    seg_list = []
    list(map(lambda cntr: seg_list.extend(cntr.segments()), input_geom_list))
    return add_slice(seg_list)

