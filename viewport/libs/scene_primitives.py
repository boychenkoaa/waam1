import numpy as np
import glm
from viewport.libs import line2poly
import struct


class GridGl:
    def __init__(self, wide, step, shader, depth=0, color=(1.0, 0.0, 0.0)):
        # draw_object.shader
        # draw_object.u_projection_location
        # draw_object.u_view_location
        # draw_object.u_transform_location
        # draw_object.vao
        # draw_object.num_triangles

        # Global variables:
        # self.projectionMat
        # self.viewMat

        self.wide = wide
        self.step = step
        self.shader = shader
        self.vao = None
        self.depth = depth
        self.color = color

        self.u_projection_location = None
        self.u_view_location = None
        self.u_transform_location = None

        self.num_vertexes = 0

        self.data = self.generate_grid(half_width=0.01)

    def generate_grid(self, half_width=0.0025):
        grid = ()
        for x in np.arange(0, self.wide, self.step):
            grid += (x - half_width, -self.wide, self.depth)
            grid += (x + half_width, -self.wide, self.depth)
            grid += (x - half_width, self.wide, self.depth)

            grid += (x + half_width, -self.wide, self.depth)
            grid += (x + half_width, self.wide, self.depth)
            grid += (x - half_width, self.wide, self.depth)

            if x != 0:
                grid += (-x - half_width, -self.wide, self.depth)
                grid += (-x + half_width, -self.wide, self.depth)
                grid += (-x - half_width, self.wide, self.depth)

                grid += (-x + half_width, -self.wide, self.depth)
                grid += (-x + half_width, self.wide, self.depth)
                grid += (-x - half_width, self.wide, self.depth)

        for y in np.arange(0, self.wide, self.step):
            grid += (-self.wide, y - half_width, self.depth)
            grid += (self.wide, y - half_width, self.depth)
            grid += (-self.wide, y + half_width, self.depth)

            grid += (self.wide, y - half_width, self.depth)
            grid += (self.wide, y + half_width, self.depth)
            grid += (-self.wide, y + half_width, self.depth)

            if y != 0:
                grid += (-self.wide, -y - half_width, self.depth)
                grid += (self.wide, -y - half_width, self.depth)
                grid += (-self.wide, -y + half_width, self.depth)

                grid += (self.wide, -y - half_width, self.depth)
                grid += (self.wide, -y + half_width, self.depth)
                grid += (-self.wide, -y + half_width, self.depth)

        self.num_vertexes = int(len(grid)/3)
        grid = np.array(grid, dtype=np.float32)

        return grid

    def regenerate_grid(self, wide, step):
        self.wide = wide
        self.step = step

        self.data = self.generate_grid(half_width=wide/1000)

    # def regenerate_grid(self, zoom):
    #     print(int(zoom))
    #     zoom = int((zoom+4)/4)
    #     # self.wide = wide
    #     self.step = zoom/2
    #     half_width = zoom/400
    #     print(half_width)
    #     self.data = self.generate_grid(half_width=half_width)


# class PolyLineGL:
#     # def __init__(self, line, shader, vao, color):
#     def __init__(self, line, shader, color):
#         self.line = line
#         self.pLine = line2poly.PLine(self.line.copy(), 0.01)
#
#         self.data = self.pLine.get_triangles()
#         self.num_triangles = int(len(self.data)/3)
#         self.data = np.array(self.data, dtype=np.float32)
#
#         self.shader = shader
#
#         self.u_projection_location = None
#         self.u_view_location = None
#         self.u_transform_location = None
#
#         self.vao = None
#         self.color = color
#
#     def add_point(self, x, y):
#         self.line.append([x, y])
#         self.pLine = line2poly.PLine(self.line.copy(), 0.01)
#
#         self.data = self.pLine.get_triangles()
#         self.num_triangles = int(len(self.data) / 3)
#         self.data = np.array(self.data, dtype=np.float32)


class PolyLinesGL:
    def __init__(self, lines, shader, color):
        self.pLine = [None] * len(lines)
        self.lines = lines

        self.data = ()
        self.num_vertexes = 0

        for line in lines:
            # self.pLine.append(line2poly.PLine(line.copy(), 0.005, align="c"))
            # tmp_data = self.pLine[-1].get_triangles()
            #
            self.pLine.append(line2poly.PLine(line.copy(), 0.005, end_fillet_res=4))
            tmp_data, num_vert = self.pLine[-1].get_triangles()

            self.data += tmp_data
            self.num_vertexes += num_vert

        # self.data = self.pLine.get_triangles()
        # self.num_triangles = int(len(self.data) / 3)
        self.data = np.array(self.data, dtype=np.float32)

        self.shader = shader

        self.u_projection_location = None
        self.u_view_location = None
        self.u_transform_location = None

        self.vao = None
        self.color = color

    # def redraw_lines(self, lines):
    #     self.pLine = [None] * len(lines)
    #     self.lines = lines
    #
    #     self.data = ()
    #     self.num_vertexes = 0
    #
    #     for line in lines:
    #         self.pLine.append(line2poly.PLine(line.copy(), 0.005, end_fillet_res=2))
    #         tmp_data, num_vert = self.pLine[-1].get_triangles()
    #         self.data += tmp_data
    #         # self.num_triangles += int(len(tmp_data) / 3)
    #     self.data = np.array(self.data, dtype=np.float32)


class MeshGL:
    def __init__(self, mesh, shader, color):
        self.mesh = mesh
        self.shader = shader

        self.u_projection_location = None
        self.u_view_location = None
        self.u_transform_location = None

        self.vao = None
        self.color = color

        self.data = ()
        self.num_vertexes = 0

        self.num_vertexes += int(len(self.mesh) / 6)

        self.data = np.array(self.mesh, dtype=np.float32)


class RectangleGL:
    def __init__(self, side_size, height, shader, color):
        self.side_size = side_size
        self.height = height

        data = ()
        data += (-side_size / 2, -side_size / 2, self.height)
        data += (side_size / 2, -side_size / 2, self.height)
        data += (-side_size / 2, side_size / 2, self.height)

        data += (-side_size / 2, side_size / 2, self.height)
        data += (side_size / 2, -side_size / 2, self.height)
        data += (side_size / 2, side_size / 2, self.height)

        data += (side_size / 2, -side_size / 2, -self.height)
        data += (-side_size / 2, -side_size / 2, -self.height)
        data += (-side_size / 2, side_size / 2, -self.height)

        data += (side_size / 2, -side_size / 2, -self.height)
        data += (-side_size / 2, side_size / 2, -self.height)
        data += (side_size / 2, side_size / 2, -self.height)

        # data += (0, 0, height)
        # data += (side_size / 2, 0, height)
        # data += (0, side_size / 2, height)
        #
        # data += (0, side_size / 2, height)
        # data += (side_size / 2, 0, height)
        # data += (side_size / 2, side_size / 2, height)

        self.num_vertexes = int(len(data)/3)
        self.data = np.array(data, dtype=np.float32)

        self.shader = shader

        self.u_projection_location = None
        self.u_view_location = None
        self.u_transform_location = None

        self.vao = None
        self.color = color

    def regenerate_rectangle(self, side_size):
        self.side_size = side_size
        data = ()
        data += (-side_size / 2, -side_size / 2, self.height)
        data += (side_size / 2, -side_size / 2, self.height)
        data += (-side_size / 2, side_size / 2, self.height)

        data += (-side_size / 2, side_size / 2, self.height)
        data += (side_size / 2, -side_size / 2, self.height)
        data += (side_size / 2, side_size / 2, self.height)

        data += (side_size / 2, -side_size / 2, -self.height)
        data += (-side_size / 2, -side_size / 2, -self.height)
        data += (-side_size / 2, side_size / 2, -self.height)

        data += (side_size / 2, -side_size / 2, -self.height)
        data += (-side_size / 2, side_size / 2, -self.height)
        data += (side_size / 2, side_size / 2, -self.height)
        self.num_vertexes = int(len(data) / 3)
        self.data = np.array(data, dtype=np.float32)


class MeshSTLGL:
    def __init__(self, filename, shader, color, scale=1, rotation=(0, 0, 0)):
        self.filename = filename
        self.rotation = rotation

        self.shader = shader

        self.u_projection_location = None
        self.u_view_location = None
        self.u_transform_location = None
        self.u_color_location = None

        self.vao = None
        self.color = color
        filename = "viewport/" + filename
        model = open(filename, mode='rb')
        model.read(80)

        num_bytes = model.read(4)

        num_bytes = int.from_bytes(num_bytes, "little", signed=True)

        self.vert_data = []

        for i in range(num_bytes):
            normalX = struct.unpack('f', model.read(4))[0]
            normalY = struct.unpack('f', model.read(4))[0]
            normalZ = struct.unpack('f', model.read(4))[0]

            tmp_norm_vec = glm.vec3(normalX, normalY, normalZ)
            tmp_norm_vec = glm.rotateX(tmp_norm_vec, rotation[0])
            tmp_norm_vec = glm.rotateY(tmp_norm_vec, rotation[1])
            tmp_norm_vec = glm.rotateZ(tmp_norm_vec, rotation[2])

            for j in range(3):
                vertX = struct.unpack('f', model.read(4))[0]
                vertY = struct.unpack('f', model.read(4))[0]
                vertZ = struct.unpack('f', model.read(4))[0]

                tmp_vert_vec = glm.vec3(vertX, vertY, vertZ)
                tmp_vert_vec = glm.rotateX(tmp_vert_vec, rotation[0])
                tmp_vert_vec = glm.rotateY(tmp_vert_vec, rotation[1])
                tmp_vert_vec = glm.rotateZ(tmp_vert_vec, rotation[2])

                self.vert_data.append(tmp_vert_vec.x)
                self.vert_data.append(tmp_vert_vec.y)
                self.vert_data.append(tmp_vert_vec.z)
                self.vert_data.append(tmp_norm_vec.x)
                self.vert_data.append(tmp_norm_vec.y)
                self.vert_data.append(tmp_norm_vec.z)
            model.read(2)

        self.vert_data = tuple(self.vert_data)

        vert_data_scaled = []
        for point in self.vert_data:
            vert_data_scaled.append(point * scale)
        vert_data_scaled = tuple(vert_data_scaled)

        self.num_vertexes = int(len(vert_data_scaled) / 6)
        self.data = np.array(vert_data_scaled, dtype=np.float32)

    def regenerate_meshstl(self, scale):
        vert_data_scaled = []
        for point in self.vert_data:
            vert_data_scaled.append(point*scale)

        vert_data_scaled = tuple(vert_data_scaled)

        self.num_vertexes = int(len(vert_data_scaled) / 6)
        self.data = np.array(vert_data_scaled, dtype=np.float32)
