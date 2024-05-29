import requests
from route import Route
import route


class LBSServer:
    def __init__(self, key="3bf4992397329e61be6b62a1399a2145"):
        self.origin = None
        self.direction_transit_url = 'https://restapi.amap.com/v3/direction/transit/integrated'
        self.key = key

    def query(self, start, destination, city_name) -> tuple[bool, Route | list]:
        start_str = f'{start[0]},{start[1]}'
        end_str = f'{destination[0]},{destination[1]}'
        param = {
            'key': self.key,
            'origin': start_str,
            'destination': end_str,
            'city': city_name,
            'cityd': city_name,
        }
        response = requests.get(self.direction_transit_url, params=param)
        res = route.parse_route_json(response.json())
        if len(res) > 0:
            return True, res[0]
        else:
            return False, []

