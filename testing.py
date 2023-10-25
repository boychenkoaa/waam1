from base.geom.algo.skeleton import gg_skeleton
from draw.draw import *
from base.geom.primitives.linear import Polygon
poly = [(0,0), (0,20), (20,10), (1,0)]
holes = [[(1,1), (2,1), (2,2), (1,2)]]
sk = gg_skeleton(poly, holes = holes)
sk1 = sk.clreturnipping(1)

plot_primitive(sk, color="red", linestyle='dotted')
plot_primitive(Polygon(poly, holes), color="black")
plot_primitive(sk1, color="blue")

plt.show()