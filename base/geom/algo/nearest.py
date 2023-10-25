from base.geom.raw.raw import distance_pp, vec, Segment, distance_seg_p

# переделать, хотим ind всегда предыдущей точки
# (id, расстояние до id) + расстояние от заданной до найденной точки
def nearest(primitive, point, area=1, only_from_existing=False):
    nearest_point = None
    min_dist = float('inf')
    for p in primitive.points():
        dist = distance_pp(p, point)
        if dist < min_dist:
            min_dist = dist
            nearest_point = p
    nearest_point = (primitive.find(nearest_point), 0)
    if only_from_existing:
        return (nearest_point, min_dist) if min_dist <= area else (None, None)
    else:  # хотим получить не просто координату, а номер начальной точки ребра и расстояние от неё до полученной точки
        # тут проверяем перпендикуляры к отрезкам, если они есть
        for near_id, seg in enumerate(primitive.segments()):
            vector = vec(seg[0], seg[1])
            segment = Segment(seg[0], vector)
            point_on_seg, dist = distance_seg_p(segment, point)
            if dist < min_dist:
                min_dist = dist
                d = distance_pp(seg[0], point_on_seg)
                nearest_point = (near_id, d)
        return (nearest_point, min_dist) if min_dist <= area else (None, None)  # хотим ближайший индекс, а не id!