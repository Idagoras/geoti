from pyproj import Proj, transform

# 定义转换器：从经纬度坐标系到 WGS84 坐标系
wgs84 = Proj(init='epsg:4326')

# 定义转换器：从 WGS84 坐标系到经纬度坐标系
utm = Proj(init='epsg:3857')


def utm_to_wgs84(pos):
    x, y = transform(utm, wgs84, pos[0], pos[1])
    return x, y


def wgs84_to_utm(pos):
    lon, lat = transform(wgs84, utm, pos[0], pos[1])
    return lon, lat


'''
ORIGIN = (113.264499, 23.130061)
p1 = (113.22803,23.209984)
op = wgs84_to_utm(ORIGIN)
op1 = wgs84_to_utm(p1)
print(f"m:{op1[0]-op[0]},n:{op1[1]-op[1]}")
'''
