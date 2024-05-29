import lbs
import route
import util.transform
from db.store import Store
"""
m = 2000  # unit = m
n = 2000  # unit = m

lbs_server = lbs.LBSServer("3bf4992397329e61be6b62a1399a2145")
_, route1_json = lbs_server.query_transit_direction([113.37655, 23.04611], [113.41557, 23.119307], "guangzhou")
_, route2_json = lbs_server.query_transit_direction([113.37655, 23.04611], [113.41157, 22.938572], "guangzhou")
route1 = route.parse_route_json(route1_json)[0]
route2 = route.parse_route_json(route2_json)[0]

print(route.Longest_Common_Sub_Sequence(route1, route2, 0.01, 0.01))

# store = Store(["guangzhou"])

# stops = store.stops("guangzhou")
# for stop in stops:
# store.add_point_to_bucket("guangzhou", ( "BV10262643",113.8125, 22.987833), m, n)

# print("hello world")
"""