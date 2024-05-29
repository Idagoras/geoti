import math
import networkx as nx
import folium
import util.transform as transform
from db.store import Store

origin = [23.130061, 113.264499]
utm_origin = transform.wgs84_to_utm((origin[1], origin[0]))


def get_bucket_boundary(m, n, u_origin, point):
    point_x, point_y = transform.wgs84_to_utm(point)
    top_left_x = u_origin[0] + m * math.floor(abs(point_x - u_origin[0]) / m) * 1 if point_x > u_origin[0] else -1
    top_left_y = u_origin[1] + n * math.floor(abs(point_y - u_origin[1]) / n) * 1 if point_y > u_origin[1] else -1
    bottom_right_x = u_origin[0] + m * math.ceil(abs(point_x - u_origin[0]) / m) * 1 if point_x > u_origin[0] else -1
    bottom_right_y = u_origin[1] + n * math.ceil(abs(point_y - u_origin[1]) / n) * 1 if point_y > u_origin[1] else -1
    top_left = transform.utm_to_wgs84((top_left_x, top_left_y))
    bottom_right = transform.utm_to_wgs84((bottom_right_x, bottom_right_y))
    return (top_left[1], top_left[0]), (bottom_right[1], bottom_right[0])


m = folium.Map(
    location=[23.130061, 113.264499],
    tiles='https://webrd02.is.autonavi.com/appmaptile?lang=en&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
    attr='高德-纯英文对照',
    zoom_start=10,
)

store = Store(['guangzhou'])
start_stop = ['BV11589187', 113.272804, 23.312162]
destination_stop = ["BV10019585", 113.35169, 23.13555]
start_bucket_points = store.points_in_same_bucket("guangzhou", 2000, 2000, start_stop)
destination_bucket_points = store.points_in_same_bucket("guangzhou", 2000, 2000, destination_stop)

for point in start_bucket_points:
    folium.Marker([point[2][1], point[2][0]], popup=point[0], icon=folium.Icon(color='blue')).add_to(m)

for point in destination_bucket_points:
    folium.Marker([point[2][1], point[2][0]], popup=point[0], icon=folium.Icon(color='red')).add_to(m)
st_top_left, st_bottom_right = get_bucket_boundary(2000,2000,utm_origin,[start_stop[1],start_stop[2]])
des_top_left, des_bottom_right = get_bucket_boundary(2000,2000,utm_origin,[destination_stop[1],destination_stop[2]])
st_rectangle = folium.Rectangle(bounds=[st_top_left,st_bottom_right],color='blue')
des_rectangle = folium.Rectangle(bounds=[des_top_left,des_bottom_right],color='red')
m.add_child(st_rectangle)
m.add_child(des_rectangle)
m.save('geo_bucket.html')
