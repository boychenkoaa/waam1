import struct

from datetime import datetime

from PyQt6.QtGui import QMatrix4x4
import math
import glm
import base.geom.raw.raw


eps = base.geom.raw.raw.EPSILON


class Triangle:
    def __init__(self, vert1, vert2, vert3):
        self.vert1 = vert1
        self.vert2 = vert2
        self.vert3 = vert3

        self.vert1_glm = glm.vec4(self.vert1[0], self.vert1[1], self.vert1[2], 1.0)
        self.vert2_glm = glm.vec4(self.vert2[0], self.vert2[1], self.vert2[2], 1.0)
        self.vert3_glm = glm.vec4(self.vert3[0], self.vert3[1], self.vert3[2], 1.0)

        self.vert1_glm_transformed = None
        self.vert2_glm_transformed = None
        self.vert3_glm_transformed = None

    def transform(self, transform_mat):
        self.vert1_glm_transformed = transform_mat * self.vert1_glm
        self.vert2_glm_transformed = transform_mat * self.vert2_glm
        self.vert3_glm_transformed = transform_mat * self.vert3_glm

    def cross_section_with_plane(self, z_cross_section):
        if (self.vert1_glm_transformed[2] > (z_cross_section+eps)) and\
           (self.vert2_glm_transformed[2] > (z_cross_section+eps)) and\
           (self.vert3_glm_transformed[2] > (z_cross_section+eps)):
            return None
        if (self.vert1_glm_transformed[2] < (z_cross_section-eps)) and\
           (self.vert2_glm_transformed[2] < (z_cross_section-eps)) and \
           (self.vert3_glm_transformed[2] < (z_cross_section-eps)):
            return None

        intersept_points = []
        tmp_intersections = self._intercept_line_with_plane(self.vert1_glm_transformed, self.vert2_glm_transformed, z_cross_section)
        if tmp_intersections is not None:
            if len(tmp_intersections) == 1:
                intersept_points.append(tmp_intersections[0])
            elif len(tmp_intersections) == 2:
                intersept_points.append(tmp_intersections[0])
                intersept_points.append(tmp_intersections[1])

        tmp_intersections = self._intercept_line_with_plane(self.vert1_glm_transformed, self.vert3_glm_transformed, z_cross_section)
        if tmp_intersections is not None:
            if len(tmp_intersections) == 1:
                intersept_points.append(tmp_intersections[0])
            elif len(tmp_intersections) == 2:
                intersept_points.append(tmp_intersections[0])
                intersept_points.append(tmp_intersections[1])

        tmp_intersections = self._intercept_line_with_plane(self.vert2_glm_transformed, self.vert3_glm_transformed, z_cross_section)
        if tmp_intersections is not None:
            if len(tmp_intersections) == 1:
                intersept_points.append(tmp_intersections[0])
            elif len(tmp_intersections) == 2:
                intersept_points.append(tmp_intersections[0])
                intersept_points.append(tmp_intersections[1])

        #  Delete duplicates points in list
        optimized_intercept_points = []
        # for point in intersept_points:
        #     if point not in optimized_intercept_points:
        #         optimized_intercept_points.append(point)

        for point in intersept_points:
            point_not_in_list = True
            for opt_point in optimized_intercept_points:
                if abs(opt_point[0]-point[0]) < eps:
                    if abs(opt_point[1] - point[1]) < eps:
                        point_not_in_list = False
                        break

            if point_not_in_list:
                optimized_intercept_points.append(point)

        return optimized_intercept_points

    def _intercept_line_with_plane(self, point1, point2, z_level):
        if (point1.z > (z_level + eps)) and (point2.z > (z_level + eps)):
            return None
        if (point1.z < (z_level - eps)) and (point2.z < (z_level - eps)):
            return None

        direction = point1 - point2

        if abs(direction.z) < eps:
            if (abs(point1.z-z_level) < eps) or (abs(point2.z-z_level) < eps):
                intersect_point = [(point1.x, point1.y), (point2.x, point2.y)]
                return intersect_point
            else:
                return None

        if abs(direction.x) < eps:
            if abs(direction.y) < eps:
                intersect_point = [((point1.x + point2.x)/2.0, (point1.y + point2.y)/2.0)]
                return intersect_point
            else:
                tmp_a = (point1.z - point2.z)/(point1.y - point2.y)
                tmp_b = point1.z - tmp_a * point1.y
                intersect_point = [((point1.x + point2.x)/2.0, (z_level-tmp_b)/tmp_a)]
                return intersect_point

        if abs(direction.y) < eps:
            tmp_a = (point1.z - point2.z)/(point1.x - point2.x)
            tmp_b = point1.z - tmp_a * point1.x
            intersect_point = [((z_level-tmp_b) / tmp_a, (point1.y + point2.y) / 2.0)]
            return intersect_point

        intersect_point = [(-(direction.x / direction.z) * point1.z + point1.x,
                            -(direction.y / direction.z) * point1.z + point1.y)]
        return intersect_point


class ModelMesh:
    def __init__(self):
        self.num_triangles = 0
        self.triangles = []

        self.intersection_points = []
        self.intersection_line_segments = []
        self.intersection_triangles = []

    def add_triangle(self, triangle):
        self.triangles.append(triangle)
        self.num_triangles += 1

    def make_slice(self, transform_mat):
        transform_mat_glm = glm.mat4(transform_mat.row(0).x(), transform_mat.row(1).x(), transform_mat.row(2).x(), transform_mat.row(3).x(),
                                     transform_mat.row(0).y(), transform_mat.row(1).y(), transform_mat.row(2).y(), transform_mat.row(3).y(),
                                     transform_mat.row(0).z(), transform_mat.row(1).z(), transform_mat.row(2).z(), transform_mat.row(3).z(),
                                     transform_mat.row(0).w(), transform_mat.row(1).w(), transform_mat.row(2).w(), transform_mat.row(3).w())

        self.intersection_points.clear()
        self.intersection_line_segments.clear()
        self.intersection_triangles.clear()

        num_crossections = 0
        for triangle in self.triangles:
            triangle.transform(transform_mat_glm)
            cs_points = triangle.cross_section_with_plane(0)

            if cs_points is not None:
                num_crossections += 1
                if len(cs_points) == 1:
                    # Single point
                    self.intersection_points.append(cs_points[0])
                if len(cs_points) == 2:
                    # Line segment
                    self.intersection_line_segments.append(cs_points)
                if len(cs_points) == 3:
                    # Triangle
                    tmp = cs_points
                    tmp.append(cs_points[0])
                    self.intersection_line_segments.append(tmp)
                    # self.intersection_line_segments.append(cs_points.append(cs_points[0]))
                    self.intersection_triangles.append(cs_points)
        # print("Num cs", num_crossections)
        return self.intersection_line_segments


class WAAMmodel:
    def __init__(self, filename, scale=1):
        self._model_filename = filename

        self.stl_model = STLmodel(self._model_filename, scale=scale)

        self.waammodel_mesh = self.stl_model.vert_data

        self.model_transform_mat = QMatrix4x4()
        self.model_transform_mat.setToIdentity()

        self.current_slice = None

        self.model_size_rank = max(self.stl_model.max_x - self.stl_model.min_x,
                                   self.stl_model.max_y - self.stl_model.min_y,
                                   self.stl_model.max_z - self.stl_model.min_z)
        self.model_size_rank = self.model_size_rank * math.sqrt(2)

    def transform_model_position(self, rot_x, rot_y, rot_z, tr_x=0, tr_y=0, tr_z=0):
        self.model_transform_mat.setToIdentity()
        self.model_transform_mat.translate(tr_x, tr_y, tr_z)
        self.model_transform_mat.rotate(rot_x, 1, 0, 0)
        self.model_transform_mat.rotate(rot_y, 0, 1, 0)
        self.model_transform_mat.rotate(rot_z, 0, 0, 1)

    def make_slice(self, transform_mat):
        self.current_slice = self.stl_model.model_mesh.make_slice(transform_mat)
        return self.current_slice

    @property
    def filename(self):
        return self._model_filename


class STLmodel:
    def __init__(self, filename, scale=1):
        self.model_mesh = ModelMesh()

        self.filename = filename
        model = open(filename, mode='rb')
        model.read(80)

        self.min_x, self.max_x = 10000.0, -10000.0
        self.min_y, self.max_y = 10000.0, -10000.0
        self.min_z, self.max_z = 10000.0, -10000.0

        num_bytes = model.read(4)

        num_bytes = int.from_bytes(num_bytes, "little", signed=True)

        self.vert_data = []

        dt1 = datetime.now()
        dt1.microsecond

        for i in range(num_bytes):
            normalX = struct.unpack('f', model.read(4))[0]
            normalY = struct.unpack('f', model.read(4))[0]
            normalZ = struct.unpack('f', model.read(4))[0]
            tmp_triangle = []

            for j in range(3):
                vertX = struct.unpack('f', model.read(4))[0]/scale
                vertY = struct.unpack('f', model.read(4))[0]/scale
                vertZ = struct.unpack('f', model.read(4))[0]/scale
                self.vert_data.append(vertX)
                self.vert_data.append(vertY)
                self.vert_data.append(vertZ)
                tmp_triangle.append([vertX, vertY, vertZ])

                if self.max_x < vertX:
                    self.max_x = vertX
                if self.min_x > vertX:
                    self.min_x = vertX

                if self.max_y < vertY:
                    self.max_y = vertY
                if self.min_y > vertY:
                    self.min_y = vertY

                if self.max_z < vertZ:
                    self.max_z = vertZ
                if self.min_z > vertZ:
                    self.min_z = vertZ

                self.vert_data.append(normalX)
                self.vert_data.append(normalY)
                self.vert_data.append(normalZ)

            model.read(2)

            self.model_mesh.add_triangle(Triangle(tmp_triangle[0],
                                                  tmp_triangle[1],
                                                  tmp_triangle[2]))

        self.vert_data = tuple(self.vert_data)

        dt2 = datetime.now()
        dt2.microsecond

        print("Open model time:", dt2-dt1)