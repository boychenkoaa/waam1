import shapely.geometry
# from shapely import MultiPolygon, LineString

from base.geom.algo.skeleton import gg_skeleton
from shapely import MultiPolygon
from base.geom.primitives.linear import Polygon, Contour, PointChain, PLine
from matplotlib import pyplot as plt
import geopandas as gpd

from draw.draw import plot_primitive, converter


big_offcuts = []  # для рисунка

# устаревшая версия, не использовать
def smart_buffer(input_geoms, distance, **kwargs):
    # **kwargs - доп параметры: resolution, cap_style, join_style, mitre_limit
    # работает для полигонов и контуров, необходимо доделать
    output_primitives = []
    for geom in input_geoms:
        shapely_geom = geom.convert_to_shapely()  # poly = Polygon([(0, 0), (1, 1), (1, 0)])
        """
        my_poly = gpd.GeoSeries([shapely_geom])
        my_poly.plot()
        """
        # shapely_geom_list = convert_geom if type(geom) == PointChain else [convert_geom]
        buffered = shapely_geom.buffer(distance, single_sided=True, **kwargs)
        """
        my_poly = gpd.GeoSeries([buffered])
        my_poly.plot()
        """
        buffered_list = list(buffered.geoms) if hasattr(buffered, 'geoms') else [buffered]
        primitive_list = []
        for prim in buffered_list:
            contour = prim.exterior
            if distance < 0:
                contour_poly = shapely.geometry.Polygon(contour)
                buffered_contours = contour_poly.buffer(-abs(distance), **kwargs)
                unbuffered_contours = buffered_contours.buffer(abs(distance), **kwargs)  # проверить возможно ошибка
                # тут может быть мультипалигон, а может быть один, поэтому ошибка?
                # как работать ? ob.geoms[0]
                type_inf = type(unbuffered_contours) == MultiPolygon
                if type_inf:
                    contour_list = [unbuff_contour.exterior for unbuff_contour in unbuffered_contours.geoms]
                else:
                    contour_list = [unbuffered_contours.exterior]
            else:
                contour_list = [contour]
            if len(prim.interiors) > 0:  # если есть дырки
                interior_list = []
                for hole in prim.interiors:
                    interior_list.append(hole)
                if distance > 0:
                    new_holes = []
                    for hole in interior_list:
                        hole_poly = shapely.geometry.Polygon(hole)
                        buffered_holes = hole_poly.buffer(-abs(distance), **kwargs)
                        unbuffered_holes = buffered_holes.buffer(abs(distance), **kwargs)
                        type_inf = type(unbuffered_holes) == MultiPolygon
                        if type_inf:
                            new_holes.extend([unbuff_hole.exterior for unbuff_hole in unbuffered_holes.geoms])
                        else:
                            new_holes.extend([unbuffered_holes.exterior])
                    interior_list = new_holes
                # как понять, в какие внешние контура попали внутренние дырки ?
                for contour in contour_list:
                    """
                    new_poly = shapely.geometry.Polygon(contour, interior_list)
                    my_poly1 = gpd.GeoSeries([new_poly])
                    my_poly1.plot()
                    """
                    holes = list(map(lambda x: list(x.coords), interior_list))
                    primitive_list.append(Polygon(contour.coords[:], holes))
            else:   # если дыр нет
                for contour in contour_list:
                    """
                    new_poly = shapely.geometry.Polygon(contour)
                    my_poly1 = gpd.GeoSeries([new_poly])
                    my_poly1.plot()
                    """
                    primitive_list.append(Contour(contour.coords[:]))
        output_primitives.extend(primitive_list)
        plt.show()
    return output_primitives


def buffer_with_shrink(input_geom, distance, **kwargs):
    # **kwargs - доп параметры: resolution, cap_style, join_style, mitre_limit
    # получить из геом-объекта поточечный список точка, линия, полигон с дырками и без
    convert_geom = input_geom.convert_to_shapely()
    """
    my_poly2 = gpd.GeoSeries([convert_geom])
    my_poly2.plot()
    """
    cap_st = kwargs.pop('cap_style', 'round')
    single = kwargs.pop('single_sided', True)
    rounding_factor = kwargs.pop('rounding_factor')
    offcut_threshold = kwargs.pop('offcut_threshold')

    buffered = convert_geom.buffer(distance, cap_style=cap_st, single_sided=single, **kwargs)  #  join_style='mitre',
    """
    my_poly3 = gpd.GeoSeries([buffered])
    my_poly3.plot()
    """

    # rounding_factor - коэффициент от которого зависит степень скругления
    shrinked = buffered.buffer(-rounding_factor, single_sided=True)
    exploded = shrinked.buffer(rounding_factor, single_sided=True)
    # if not exploded:  -  добавить скелет

    """
    my_poly4 = gpd.GeoSeries([exploded])
    my_poly4.plot()
    """

    buffered_list = list(exploded.geoms) if hasattr(exploded, 'geoms') else [exploded]
    # вычислить разность buffered - exploded
    """
    offcuts = buffered.difference(exploded)  # polygon / multipolygon
    pl_sh_list = []
    
    if offcuts:
        offcuts_list = list(offcuts.geoms) if hasattr(offcuts, 'geoms') else [offcuts]
        for offcut in offcuts_list:
            if offcut.area > offcut_threshold:
                big_offcuts.append(offcut)
                s = offcut.convex_hull.exterior.coords[:]
                gg_offcut = gg_skeleton(s)  # геом граф
                plines = converter.do(gg_offcut)

                for pl in plines:
                    # для исключения точек качания, подумать над реализацией!!
                    intrsct_lines = LineString(pl).intersection(offcuts.buffer(-rounding_factor/8, single_sided=True))
                    intrsct_list = list(intrsct_lines.geoms) if hasattr(intrsct_lines, 'geoms') else [intrsct_lines]
                    pl_sh_list.extend(intrsct_list)

                # pl_of_list.append()
                # big_offcuts_list.append(gg_skeleton(s))  # .clipping(1)
            """

    primitive_list = []
    for buff_geom in buffered_list:
        contour = buff_geom.exterior
        if len(buff_geom.interiors) > 0:
            interior_list = []
            for hole in buff_geom.interiors:
                interior_list.append(hole)
                """
                new_poly = shapely.geometry.Polygon(contour, interior_list)
                my_poly1 = gpd.GeoSeries([new_poly])
                my_poly1.plot()
                """
            holes = list(map(lambda x: list(x.coords), interior_list))
            primitive_list.append(Polygon(contour.coords[:], holes))
        elif contour.coords:  # для точки с отрицательным буфером, координат не будет!
            """
            new_poly = shapely.geometry.Polygon(contour)
            my_poly2 = gpd.GeoSeries([new_poly])
            my_poly2.plot()
            """
            primitive_list.append(Contour(contour.coords[:]))
    """
    for pl_sh in pl_sh_list:
        primitive_list.append(PLine(pl_sh.coords[:]))
        """

    # plt.show()
    return primitive_list


def buffer(input_geom, distance, **kwargs):
    # **kwargs - доп параметры: resolution, cap_style, join_style, mitre_limit
    # получить из геом-объекта объекты шейпли - линию / полигон с дырками и без (для нашего полигона и контура)
    # не рассматриваем pointchain - так как это малоприменимо
    # подумать про вырожденный случай, когда линий из одной точки

    # print(type(input_geom), input_geom)

    convert_geom = input_geom.convert_to_shapely()
    cap_st = kwargs.pop('cap_style', 'round')
    join_st = kwargs.pop('join_style', 'mitre')
    single = kwargs.pop('single_sided', True)
    """ 
    my_poly = gpd.GeoSeries([convert_geom])
    my_poly.plot()
        """
    buffered = convert_geom.buffer(distance, cap_style=cap_st, join_style=join_st, single_sided=single, **kwargs)
    buffered_list = list(buffered.geoms) if hasattr(buffered, 'geoms') else [buffered]  # случай мультиполигона
    primitive_list = []
    for buff_geom in buffered_list:
        contour = buff_geom.exterior
        if len(buff_geom.interiors) > 0:
            interior_list = []
            for hole in buff_geom.interiors:
                interior_list.append(hole)
                """
                new_poly = shapely.geometry.Polygon(contour, interior_list)
                my_poly1 = gpd.GeoSeries([new_poly])
                my_poly1.plot()
                """

            holes = list(map(lambda x: list(x.coords), interior_list))
            primitive_list.append(Polygon(contour.coords[:], holes))
        elif contour.coords:  # для точки с отрицательным буфером, координат не будет!
            """
            new_poly = shapely.geometry.Polygon(contour)
            my_poly2 = gpd.GeoSeries([new_poly])
            my_poly2.plot()
            """
            primitive_list.append(Contour(contour.coords[:]))
    # plt.show()
    return primitive_list


def serial_buffer(input_geom, distance_list, simple_buffer_tipe=True, with_difference=False, **kwargs):
    input_geom_holes = []
    if with_difference and (type(input_geom) == Polygon):  # вытаскиваем контуры проверить!
        input_geom_contours = input_geom.get_all_contours()
        input_geom = input_geom_contours[0]
        input_geom_holes = input_geom_contours[1:]  # проверить !
    algo = buffer if simple_buffer_tipe else buffer_with_shrink
    if simple_buffer_tipe:
        kwargs.pop('rounding_factor', None)
        kwargs.pop('offcut_threshold', None)
    else:
        kwargs.setdefault('rounding_factor', abs(distance_list[0]))
        kwargs.setdefault('offcut_threshold', 0.0005)  # для скелета, сейчас не используется

    input_geom_list = [input_geom]
    depth = 0
    contour_list = []
    while input_geom_list:
        new_geom_list = []
        for in_geom in input_geom_list:
            new_geom_list.extend(algo(input_geom=in_geom, distance=-distance_list[depth], **kwargs))
        input_geom_list = new_geom_list
        if depth + 1 < len(distance_list):
            depth += 1
        for geom in input_geom_list:
            if isinstance(geom, Contour) or isinstance(geom, PLine):
                contour_list.append(geom)  # Contour(geom.points())
            if isinstance(geom, Polygon):  # так как у полигона может быть несколько конутров
                for point_cont in geom.points():
                    contour_list.append(Contour(point_cont))

    """
    my_poly2 = gpd.GeoSeries(big_offcuts)
    my_poly2.plot()
        """

    if with_difference and input_geom_holes:  # вычетаем дырки
        # contour_list пересечь с input_geom_holes
        # object.difference(other)
        new_geoms = []
        sh_lines = []  # для отрисовки
        for trajectory in contour_list:
            sh_trajectory = trajectory.convert_to_shapely(boundary=True)  # получили контур
            for g_holes in input_geom_holes:
                sh_hole = g_holes.convert_to_shapely()
                sh_trajectory = sh_trajectory.difference(sh_hole)
            sh_lines.append(sh_trajectory)
            clipped_trajectory_list = list(sh_trajectory.geoms) if hasattr(sh_trajectory, 'geoms') else [sh_trajectory]
            for clipped_trajectory in clipped_trajectory_list:
                if clipped_trajectory:
                    if clipped_trajectory.coords[0] == clipped_trajectory.coords[-1]:
                        new_geoms.append(Contour(clipped_trajectory.coords[:]))
                    else:
                        new_geoms.append(PLine(clipped_trajectory.coords[:]))
        """        

        my_poly = gpd.GeoSeries(sh_lines)
        my_poly.plot()
        # new_contours.append(PLine(sh_trajectory.coords[:]))
        plt.show()
        """

        return new_geoms
    # для отрисовки
    """  
    sh_lines = []
    for trajectory in contour_list:
        sh_trajectory = trajectory.convert_to_shapely(boundary=True)
        sh_lines.append(sh_trajectory)
    my_poly = gpd.GeoSeries(sh_lines)
    my_poly.plot()
    # my_poly3 = gpd.GeoSeries(pl_sh_list)
    # my_poly3.plot()

    # for big_of in big_offcuts_list:
        # plot_primitive(big_of, color="red")
    plt.show()
      """

    return contour_list

""" 
poly = [(1, 1), (12, -2), (16, 2)]  
a = PLine(poly)  # сделать ограничение на отрицательный буфер для линий! отдельно для одной точки!
poly2 = [(1, 1), (12, -2), (16, 2), (12, 12), (1, 13), (2, 9), (0, 5), (16, 2)]  #
b = Contour(poly2)
poly1 = Polygon([(6, 1), (2, 2), (4, 5)], [[(4, 3), (4, 2), (3, 3)]])
# distance_list= -0.025, , -0.05, -0.05, -0.05, -0.05, -0.05, -0.05, -0.05, -0.05
# можно добавить доп параметры : rounding_factor, resolution, cap_style, join_style, mitre_limit
out = serial_buffer(poly1, distance_list=[0.1, 0.05], simple_buffer_tipe=False, with_difference=False)  # , rounding_factor=0.07

out2 = buffer(input_geom=poly1, distance=-0.1)


# out2 = buffer(input_geoms= out, distance=-0.1)
# out3 = buffer(input_geoms= out2, distance=-0.1)
# out4 = buffer(input_geoms= out3, distance=-0.1)
# out5 = buffer(input_geoms= out4, distance=-0.1)

geo = [b, Polygon([(6, 1), (2, 2), (4, 5)], [[(4, 3), (4, 2), (3, 3)]]), Contour([(1, 1), (1, 0), (0, 0), (0, 1)]), a]
out = buffer2(input_geoms=geo, distance=-0.2)
v  = 1
 """

