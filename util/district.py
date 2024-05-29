import requests
from shapely.geometry import Point, Polygon

GAODE_AK = '3bf4992397329e61be6b62a1399a2145'
URL = "https://restapi.amap.com/v3/config/district"


def get_district(city_name):
    params = {"key": GAODE_AK, "keywords": city_name, "extensions": "all"}
    r = requests.get(URL, params=params)
    data = r.json()
    district = data["districts"][0]["polyline"]
    domain_strs = district.split("|")
    res = []
    for domain in domain_strs:
        point_strs = domain.split(";")
        domain_p = []
        for point_str in point_strs:
            pos = point_str.split(',')
            domain_p.append((float(pos[0]), float(pos[1])))
        res.append(domain_p)
    return res


def stops_filter(districts, points):
    boundaries = [Polygon(domain) for domain in districts]
    res = []
    for point in points:
        sp = Point(point[1], point[2])
        contain = False
        for boundary in boundaries:
            contain = contain or boundary.contains(sp)
        if contain:
            res.append(point)
    return point
