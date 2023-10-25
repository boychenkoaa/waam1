# raw simple geometry
from math import acos, asin, cos, sin
from collections import namedtuple

# -------------------- constants --------------------

X, Y, Z = 0, 1, 2
K, B = 0, 1
EPSILON = 1e-4
EPSILON2 = EPSILON ** 2

# -------------------- simple types --------------------

Line = namedtuple('Line', ['p', 'v'])
Segment = namedtuple('Segment', ['p', 'v'])
Circle = namedtuple('Circle', ['center', 'R'])


# -------------------- arithmetic --------------------

def sign(x):
    ans = 0
    if x > 0:
        ans = 1
    if x < 0:
        ans = -1
    return ans


# -------------------- linalg --------------------

def kramor2(a11, a12, a21, a22, b1, b2):
    mx = b1*a22 - b2*a12
    my = b2*a11 - b1*a21
    m = a11*a22 - a21*a12
    if m == 0:
        return None
    else:
        return mx / m, my / m  # проверить !!

# -------------------- vector --------------------


def length2(v: tuple) -> float:
    return v[X] ** 2 + v[Y] ** 2


def length(v: tuple) -> float:
    return length2(v) ** 0.5


def vec(beg: tuple, end: tuple) -> tuple:
    return end[X] - beg[X], end[Y] - beg[Y]


def seg(beg: tuple, end: tuple):
    return Segment(beg, vec(beg, end))


def normalize(v: tuple) -> tuple:
    len_v = length(v)
    if len_v == 0:
        return 0, 0
    return scale(v, 1 / len_v)


def add_pv(p: tuple, v: tuple):
    return p[X] + v[X], p[Y] + v[Y]


def add_vv(v1: tuple, v2: tuple):
    return v1[X] + v2[X], v1[Y] + v2[Y]


def scale(v: tuple, k: float):
    return v[X] * k, v[Y] * k


def mul(k: float, v: tuple):
    return scale(v, k)


def angle(v1: tuple, v2: tuple) -> float:
    return acos((v1[X] * v2[X] + v1[Y] * v2[Y]) / (length(v1) * length(v2)))


def dot(v1: tuple, v2: tuple):
    return v1[X] * v2[X] + v1[Y] * v2[Y]


def skew(v1: tuple, v2: tuple):
    return v1[X] * v2[Y] - v1[Y] * v2[X]


def is_collinear(v1: tuple, v2: tuple):
    return abs(skew(v1, v2)) <= EPSILON


def mov_t(line: Line, t: float):
    return add_pv(line.p, mul(t, line.v))


# -------------------- predicates --------------------


def orient_determinant(a: tuple, b: tuple, c: tuple):
    return (a[X] - c[X]) * (b[Y] - c[Y]) - (a[Y] - c[Y]) * (b[X] - c[X])


def p_in_l(p: tuple, line: Line):
    p1 = add_pv(line.p, line.v)
    a = abs(orient_determinant(line.p, p1, p)) <= EPSILON
    return a


def p_in_s(p: tuple, s: Segment):
    begin = s.p
    end = add_pv(s.p, s.v)
    # проверить !
    x_min, x_max = (begin[X], end[X]) if begin[X] < end[X] else (end[X], begin[X])
    y_min, y_max = (begin[Y], end[Y]) if begin[Y] < end[Y] else (end[Y], begin[Y])

    return p_in_l(p, s) and ((x_min - p[X] <= EPSILON) and (p[X] - x_max <= EPSILON) and (y_min - p[Y] <= EPSILON) and (p[Y] - y_max <= EPSILON))

# -------------------- basics --------------------


def distance_pp(p1: tuple, p2: tuple):
    return ((p1[X] - p2[X]) ** 2 + (p1[Y] - p2[Y]) ** 2) ** 0.5


# расстояние от точки до прямой
def distance_line_p(line, point):  # переделать line => vector
    line_vec = vec(line[0], line[1])
    if line_vec[Y] == 0:
        x = point[0]
        y = line[0][1]
        dist = abs(point[1] - y)
    elif line_vec[X] == 0:
        x = line[0][0]
        y = point[1]
        dist = abs(point[0] - x)
    else:
        a1 = - line_vec[Y] / line_vec[X]
        x = ((line_vec[Y] * line[0][0])/line_vec[X] - point[0]/a1 + point[1] - line[0][1]) / (- a1 - (1/a1))
        y = (x - point[0])/a1 + point[1]
        dist = abs(line_vec[Y] * point[0] - line_vec[X] * point[1] + line[1][0]*line[0][1] - line[1][1]*line[0][0])/length(line_vec)
    return (x, y), dist


# переделать
def distance_seg_p(seg: Segment, point):  # seg = namedtuple('Segment', ['p', 'v'])
    v = seg.v  # vec(seg[0], seg[1])
    w0 = vec(point, seg.p)
    w1 = add_vv(v, w0)  # vec(point, seg[1])
    if dot(w0, v) >= 0:
        return seg[0], distance_pp(seg.p, point)
    if dot(w1, v) <= 0:
        return seg[1], distance_pp(add_pv(seg.p, seg.v), point)
    return distance_line_p((seg.p, add_pv(seg.p, seg.v)), point)


def rotate(point: tuple, rot_cntr: tuple, r_angle: float):
    new_x = ((point[X] - rot_cntr[X]) * cos(r_angle) - (point[Y] - rot_cntr[Y]) * sin(r_angle)) + rot_cntr[X]
    new_y = ((point[X] - rot_cntr[X]) * sin(r_angle) + (point[Y] - rot_cntr[Y]) * cos(r_angle)) + rot_cntr[Y]
    return new_x, new_y


# -------------------- intersections --------------------

# intersection between circle ((x0, y0), R) and line (px + vx*t, py + vy*t)
# equation is (vx**2 + vy**2) * t**2 + 2*(dx*vx + dy*vy)*t + dx**2 + dy**2 - R**2 = 0
# where dx = px - x0, dy = py - y0
def intersect_lc(line: Line, circle: Circle):
    vx, vy = line.v[X], line.v[Y]
    dx, dy = line.p[X] - circle.center[X], line.p[Y] - circle.center[Y]
    A = vx ** 2 + vy ** 2
    B2 = vx * dx + vy * dy
    C = dx ** 2 + dy ** 2 - circle.R ** 2
    D = B2 ** 2 - A * C
    ans = None
    if D == 0:
        t = -B2 / A
        ans = mov_t(line, t)
    elif D > 0:
        t1 = (-B2 - D ** 0.5) / A
        t2 = (-B2 + D ** 0.5) / A
        ans = [mov_t(line, t1), mov_t(line, t2)]
    return ans


def intersect_sc(segment: Segment, circle: Circle):
    lc_intersection = intersect_lc(segment, circle)
    ans = None
    if isinstance(lc_intersection, tuple):
        if p_in_s(lc_intersection, segment):
            ans = lc_intersection
    elif isinstance(lc_intersection, list):
        ans = []
        for i in (0, 1):
            if p_in_s(lc_intersection[i], segment):
                ans.append(lc_intersection[i])
        if len(ans) == 0:
            ans = None
    return ans


def intersect_ll(line1: Line, line2: Line):
    # если параллельны
    if is_collinear(line1.v, line2.v):
        return None
    else:
        a11, a12, a21, a22 = line1.v[Y], -line1.v[X], line2.v[Y], -line2.v[X]
        b1, b2 = line1.p[X] * line1.v[Y] - line1.p[Y] * line1.v[X], line2.p[X] * line2.v[Y] - line2.p[Y] * line2.v[X]
        return kramor2(a11, a12, a21, a22, b1, b2)


def intersect_sl(s: Segment, line: Line):
    p = intersect_ll(s, line)
    if not (p is None):
        if not p_in_s(p, s):
            p = None
    return p


def intersect_ss(s1: Segment, s2: Segment):
    p = intersect_ll(s1, s2)
    if not (p is None):
        if not (p_in_s(p, s1) and p_in_s(p, s2)):
            p = None
    return p


# -------------------- locus --------------------
INNER_LOCUS, BOUND_LOCUS, OUTER_LOCUS = -1, 0, 1


def locus_pc(p: tuple, circle: Circle):
    return sign(distance_pp(p, circle.center) - circle.R)


def p_in_c(p: tuple, circle: Circle):
    loc = locus_pc(p, circle)
    return (loc == INNER_LOCUS) or (loc == BOUND_LOCUS)


# -------------------- other --------------------
def mov_p_along_s(distance: float, s: Segment):
    return mov_t(s, distance / length(s.v))


def seg(p1: tuple, p2: tuple):
    return Segment(p1, vec(p1, p2))


def int_approximate(val: float):
    return round(val / EPSILON)


def kb(line: Line):
    vx, vy, px, py = line.v[X], line.v[Y], line.p[X], line.p[Y]
    return vy / vx, (vx * py - px * vy) / vx
