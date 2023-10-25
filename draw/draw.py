import matplotlib.pyplot as plt

from backend.PlineConverter import PlainConverter

converter = PlainConverter()

def plot_primitive(primitive, **params):
    plines = converter.do(primitive)
    if not plines is None:
        for pline in plines:
            x = [point[0] for point in pline]
            y = [point[1] for point in pline]
            plt.plot(x, y, **params)







