"""
a = Contour([(3, 2), (12, 5), (16, 9)])  # Contour([(2, 1), (2, 7), (4, 7)])
ap = a.points()
b = Contour([(4, 9), (4, 7), (6, 7), (6, 9)])  # Contour([(5, 1), (6, 3), (5, 8), (7, 9), (9, 5)])
c = Contour([(9, 5), (2, 5), (2, 11), (9, 11)])  # Contour([(9, 10), (11, 7), (13, 9), (11, 11)])
e = Contour([(3, 6), (7, 6), (7, 10), (3, 10)])  # Contour([(3, 6), (7, 6), (7, 10), (3, 10)])
k1 = Contour([(16, 2), (16, 9), (22, 9), (22, 2)])
k2 = Contour([(17, 3), (17, 8), (21, 8), (21, 3)])
k3 = Contour([(18, 7), (18, 5), (20, 5), (20, 7)])
ordered_collection = [a, b, c, e, k1, k2, k3]

# обернуть в одну функцию, список ломаных, список отрезков и аргумент повтора
# custom_input = [[(13, 6), (5, 8)], [(14, 6), (19, 6)], [(19, 6), (15, 10)]]  # [(13, 6), (19, 6)] , (7, 5), (12, 9), (3, 5)  # [(19, 6), (15, 10), (11, 2), (5, 8)]
# no_repeats = True  # повторное посещение
# order = get_polyline_order(ordered_collection, custom_input, no_repeats)
# print(order)

new_p = get_nearest_point(a, (8, 7))
b = 1
"""