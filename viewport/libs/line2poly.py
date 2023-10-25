import matplotlib.pyplot as plt
from math import sqrt, sin, cos, acos, pi
import numpy as np


def sign(x):
    return 1 - 2 * (x < 0)


def angle(dx, dy):
    return 2 * pi - acos(dx / (dx ** 2 + dy ** 2) ** 0.5) if dy < 0 else acos(dx / (dx ** 2 + dy ** 2) ** 0.5)


def length(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def turn_to_vectors(triangle):
    v1 = [triangle[1][0] - triangle[0][0], triangle[1][1] - triangle[0][1], 0]
    v2 = [triangle[2][0] - triangle[0][0], triangle[2][1] - triangle[0][1], 0]
    return v1, v2


def nearest(angle1, angle2, zero):
    """ Функция принимает два угла и "ноль" и возвращает угол, лежащий ближе к нулю """
    if abs(angle_dist(angle1, zero)) < abs(angle_dist(angle2, zero)):
        return angle1
    else:
        return angle2


def which_is_closer(angle1, angle2, zero):
    """ Функция принимает два угла и "ноль" и возвращает какой угол по номеру ближе к нулю """
    if abs(angle_dist(angle1, zero)) < abs(angle_dist(angle2, zero)):
        return 0
    else:
        return 1


def angle_dist(a1, a2):
    """ Функция определяет угловое расстояние между двумя углами по окружности """
    diff = (a2 - a1 + pi) % (2 * pi) - pi
    return diff if diff > -pi else diff + 2 * pi


def is_parallel(line1, line2, eps=0.01):
    """ Функция проверяет параллельность двух линий """
    return abs((line1[0][0] - line1[1][0]) * (line2[0][1] - line2[1][1]) -
               (line1[0][1] - line1[1][1]) * (line2[0][0] - line2[1][0])) < eps


def is_clockwise(triangle):
    vectors = turn_to_vectors(triangle)
    return angle_dist(angle(*vectors[0][:2]), angle(*vectors[1][:2])) < 0


def polygonize_trapezoid(pair1, pair2):
    """ Функция принимает две пары точек - координаты боковых сторон трапеции, которую она разбивает диагональю на два
        треугольника. Порядок точек меняется если основания трапеции скрещиваются, когда должны быть параллельны """
    if is_parallel([pair1[0], pair2[0]], [pair1[1], pair2[1]]):
        return [[pair1[0], pair2[0], pair2[1]], [pair1[0], pair1[1], pair2[1]]]
    return [[pair1[0], pair1[1], pair2[0]], [pair1[0], pair2[1], pair2[0]]]


# def create_cap_fillet(cap, direction, r, z, n):
#     start = angle(cap[0][0] - cap[1][0], cap[0][1] - cap[1][1])
#     center = [(cap[0][0] + cap[1][0]) / 2, (cap[0][1] + cap[1][1]) / 2]
#     dir_angle = angle(direction[0] - center[0], direction[1] - center[1])
#     angle_inc = pi / n
#     fillet = [[center[0] + r * cos(current_ang := nearest(start + angle_inc * i, start - angle_inc * i, dir_angle)),
#                center[1] + r * sin(current_ang), z] for i in range(n + 1)]
#     return [[center + [z], fillet[i], fillet[i + 1]] for i in range(len(fillet) - 1)]
def create_angle_fillet(start, bisector, center, r, z, p3, sector, n):
    start = angle(start[0] - center[0], start[1] - center[1])
    dir_angle = angle(bisector[0] - center[0], bisector[1] - center[1])
    angle_inc = sector / n
    fillet = [[center[0] + r * cos(current_ang := nearest(start + angle_inc * i, start - angle_inc * i, dir_angle)),
               center[1] + r * sin(current_ang), z] for i in range(n + 1)]
    return [[p3, fillet[i], fillet[i + 1]] for i in range(len(fillet) - 1)]


def create_cap_fillet(center, r, n, s_ang, c_ang):
    angle_inc = pi / n
    direction = 1 - 2 * which_is_closer(s_ang + angle_inc, s_ang - angle_inc, c_ang)
    points = [[center[0] + r * cos(temp_ang := s_ang + direction * angle_inc * i),
               center[1] + r * sin(temp_ang), center[2]] for i in range(n + 1)]
    return [[*face, center] for face in zip(points[:-1], points[1:])]


class PLine:
    def __init__(self, line, width, z=1, cap_res=4):
        self.cap_fillet_res = cap_res  # Число граней, составляющих скругление на концах ломаной
        self.width = width / 2
        self.z_level = z
        self.triangle_array = []
        self.trapezoid_buffer = -1
        self.points = []
        self.polygons = []
        if line:
            self.polygonize(line)

    def polygonize(self, line):
        z = self.z_level
        w = self.width
        for pair in zip(line[:-1], line[1:]):
            if pair[0] == pair[1]:
                continue
            tilt = angle(pair[1][0] - pair[0][0], pair[1][1] - pair[0][1])
            angle1 = tilt + pi / 2
            angle2 = tilt - pi / 2
            corners = [[pair[0][0] + w * cos(angle1), pair[0][1] + w * sin(angle1), z],
                       [pair[0][0] + w * cos(angle2), pair[0][1] + w * sin(angle2), z],
                       [pair[1][0] + w * cos(angle1), pair[1][1] + w * sin(angle1), z],
                       [pair[1][0] + w * cos(angle2), pair[1][1] + w * sin(angle2), z]]
            self.polygons.extend(create_cap_fillet(pair[0] + (z,), w, self.cap_fillet_res, angle1, tilt + pi))
            self.polygons.extend(polygonize_trapezoid([corners[0], corners[1]], [corners[2], corners[3]]))
            self.polygons.extend(create_cap_fillet(pair[1] + (z,), w, self.cap_fillet_res, angle1, tilt))

    # def polygonize(self, line, w, z):
    #     if line[0][0] == line[-1][0] and line[0][1] == line[-1][1]:
    #         is_open = False
    #         line = [line[-2]] + line + [line[1]]
    #     else:
    #         is_open = True
    #         angle1 = angle(line[1][0] - line[0][0], line[1][1] - line[0][1]) + pi
    #         angle2 = angle(line[-2][0] - line[-1][0], line[-2][1] - line[-1][1]) + pi
    #         line.insert(0, [line[0][0] + w / 2 * cos(angle1), line[0][1] + w / 2 * sin(angle1)])
    #         line.append([line[-1][0] + w / 2 * cos(angle2), line[-1][1] + w / 2 * sin(angle2)])
    #     caps = []
    #     for i in range(len(line) - 2):
    #         angle1 = angle(line[i][0] - line[i + 1][0], line[i][1] - line[i + 1][1])  # Угол первого звена
    #         angle2 = angle(line[i + 2][0] - line[i + 1][0], line[i + 2][1] - line[i + 1][1])  # Угол второго звена
    #         bisector = (angle1 + angle2) / 2 if abs(angle1 - angle2) > pi else \
    #             (angle1 + angle2) / 2 + pi if angle1 + angle2 < 2 * pi else (angle1 + angle2) / 2 - pi
    #         #  Угол биссектрисы двух звеньев + 180 (т.е. с "тупой" стороны)
    #         nearest1 = nearest(angle1 + pi / 2, angle1 - pi / 2, bisector)
    #         nearest2 = nearest(angle2 + pi / 2, angle2 - pi / 2, bisector)
    #         #  Углы звеньев + 90 градусов в направлении биссектрисы
    #         sector = abs(angle1 - angle2) if abs(angle1 - angle2) < pi else 2 * pi - abs(angle1 - angle2)
    #         #  Угол между звеньями
    #         corrected_w = min(w / 2 / abs(sin(bisector - angle1)), length(line[i], line[i + 1]))
    #         points = [[line[i + 1][0] + w / 2 * cos(nearest1),
    #                    line[i + 1][1] + w / 2 * sin(nearest1), z],
    #                   [line[i + 1][0] + w / 2 * cos(bisector),
    #                    line[i + 1][1] + w / 2 * sin(bisector), z],
    #                   [line[i + 1][0] + w / 2 * cos(nearest2),
    #                    line[i + 1][1] + w / 2 * sin(nearest2), z],
    #                   [line[i + 1][0] - corrected_w * cos(bisector),
    #                    line[i + 1][1] - corrected_w * sin(bisector), z],
    #                   [line[i + 1][0] + corrected_w * cos(bisector),
    #                    line[i + 1][1] + corrected_w * sin(bisector), z]]
    #         if i == 0:                                              # Первый угол в многоугольнике
    #             self.add_trapezoid([points[2], points[3]])
    #             caps.append([points[2], points[3]])
    #         elif i == len(line) - 3:                                # Последний угол в многоугольнике
    #             self.add_trapezoid([points[0], points[3]])
    #             if not is_open:
    #                 self.polygons.extend(create_angle_fillet(points[0], points[1], line[i + 1], w / 2, z, points[3],
    #                                                          sector - pi, self.angle_fillet_res))
    #             caps.append([points[0], points[3]])
    #         elif round(abs(sector - pi), 4) <= self.fillet_thresh:  # Развернутый угол
    #             self.add_trapezoid([points[3], points[4]])
    #             self.add_trapezoid([points[3], points[4]])
    #         else:
    #             self.add_trapezoid([points[0], points[3]])
    #             self.polygons.extend(create_angle_fillet(points[0], points[1], line[i + 1], w / 2, z, points[3],
    #                                                      sector - pi, self.angle_fillet_res))
    #             self.add_trapezoid([points[2], points[3]])
    #     if is_open:
    #         self.polygons[:0] = create_cap_fillet(caps[0], line[0], w / 2, z, self.cap_fillet_res)
    #         self.polygons.extend(create_cap_fillet(caps[1], line[-1], w / 2, z, self.cap_fillet_res))

    def add_trapezoid(self, line):
        if self.trapezoid_buffer == -1:
            self.trapezoid_buffer = len(self.polygons)
            self.polygons.append(line)
        else:
            self.polygons[self.trapezoid_buffer:self.trapezoid_buffer + 1] = \
                polygonize_trapezoid(self.polygons[self.trapezoid_buffer], line)
            self.trapezoid_buffer = -1

    # def get_triangles(self):
    #     self.points = np.array(self.polygons, dtype=np.float32)
    #     self.points = self.points.flatten()
    #     return self.points, len(self.points)
    #

    def get_triangles(self):
        data = ()
        for triangle in self.polygons:
            if is_clockwise(triangle):
                triangle[1], triangle[2] = triangle[2], triangle[1]
            for point in triangle:
                data += tuple(point)
        return data, len(data)

    def plot(self):
        [plt.plot([p[0][0], p[1][0], p[2][0], p[0][0]], [p[0][1], p[1][1], p[2][1], p[0][1]]) for p in self.polygons]


lines1 = [[0, 0], [0, 25], [0, -25], [0, -25]]
lines2 = [[0, -25], [10, 10], [-30, 10]]

#lines = [[0, 0], [1, 1.5], [2, 0], [0, 0]]
#lines = [[-1, -1], [-1, 1], [-1, 3]]
#lines = [[0, 0], [1, 1], [2, 0]]

if __name__ == "__main__":
    pLine = PLine([], 5, cap_res=5)
    pLine.polygonize(lines1.copy())
    pLine.polygonize(lines2.copy())
    # pLine.get_triangles()
    # plt.plot([el[0] for el in lines], [el[1] for el in lines])
    pLine.plot()
    triangles = pLine.get_triangles()[0]
    plt.scatter([triangles[i] for i in range(0, len(triangles) - 2, 3)],
                [triangles[i] for i in range(1, len(triangles) - 1, 3)])

    plt.axis("equal")
    plt.show()
