from pyecharts.charts import Geo
from pyecharts.globals import GeoType
from pyecharts import options as opts

import util.district
from db.store import Store
from shapely.geometry import Point, Polygon


def draw_geo_scatter_plot(city_name, pts):
    g = Geo()
    g.add_schema(maptype=city_name,is_roam=True)
    data_pair = []
    for pt in pts:
        g.add_coordinate(pt[0], pt[1], pt[2])
        data_pair.append((pt[0], 0))
    g.add('', data_pair=data_pair, type_=GeoType.SCATTER, symbol_size=3,is_large=True)
    g.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    pieces = [
        {'max': 1, 'label': "公交站点（包括地铁站）", "color": "#50A3BA"}
    ]
    g.set_global_opts(title_opts=opts.TitleOpts(title="{} 公交站点分布".format(city_name)),
                      )
    return g


store = Store(["guangzhou"])
points = store.stops("guangzhou")
p = util.district.get_district("广州")
city_boundaries = [Polygon(domain) for domain in util.district.get_district("广州")]
city_stops = []
for point in points:
    #print(points)
    city_stop = Point(point[1][1], point[1][0])
    contain = False
    for city_boundary in city_boundaries:
        contain = contain or city_boundary.contains(city_stop)
    #if contain:
    city_stops.append((point[0], point[1][0], point[1][1]))
print(len(city_stops))
print(len(points))

g = draw_geo_scatter_plot("广州", city_stops)
g.render('test_guangzhou.html')
