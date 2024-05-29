from model.stop import Stop
from enum import Enum



class TransportationType(Enum):
    TRAIN = 1
    AIRPLANE = 2
    BUS = 3
    CAR = 4
    WALK = 5
    COACH = 6


class BusStep:
    def __init__(self, departure_stop_id, arrival_stop_id, line_id, polyline, distance, duration, via_stops_id):
        self.departure_stop_id = departure_stop_id
        self.arrival_stop_id = arrival_stop_id
        self.line_id = line_id
        self.polyline = polyline
        self.distance = distance
        self.duration = duration
        self.via_stops_id = via_stops_id

    def __str__(self):
        obj_description = f'line : {self.line_id} >>{self.departure_stop_id} -> {self.arrival_stop_id};\n + via stops:'
        for via_stop in self.via_stops_id:
            obj_description += f'{via_stop},'
        obj_description = obj_description[:-1]
        obj_description += f' \n Polyline: {self.polyline}'
        return obj_description


class WalkingStep:
    def __init__(self, origin, destination, polyline, distance, duration, sequences):
        self.origin = origin
        self.destination = destination
        self.polyline = polyline
        self.distance = distance
        self.duration = duration
        self.sequences = sequences

    def __str__(self):
        obj_description = (f"Origin: {self.origin} -> Destination: {self.destination}; Distance: {self.distance}; "
                        f"Duration: {self.duration}\n Polyline:{self.polyline}")
        return obj_description


class RouteSegment:
    def __init__(self, walking_step, bus_step):
        self.walking_step = walking_step
        self.bus_step = bus_step

    def __str__(self):
        obj_description = ''
        if isinstance(self.walking_step, WalkingStep):
            obj_description += 'Walking Step:' + str(self.walking_step) + '\n'
        if isinstance(self.bus_step, BusStep):
            obj_description += 'Bus Step:' + str(self.bus_step) + ';'
        return obj_description


class Route:
    def __init__(self, origin, destination, distance, duration, price):
        self.origin = origin
        self.destination = destination
        self.distance = distance
        self.duration = duration
        self.price = price
        self.segments = []

    def add_segment(self, segment):
        self.segments.append(segment)

    def __str__(self):
        obj_description = f'{self.origin} -> {self.destination}; distance: {self.distance}; duration: {self.duration}; price: {self.price}' + '\n'
        for i, segment in enumerate(self.segments):
            obj_description += f'segment {i}: ' + str(segment) + '\n'
        return obj_description

    def get_polyline(self):
        res = []
        for segment in self.segments:
            walking_step_polyline = segment.walking_step.polyline + ";" if isinstance(segment.walking_step,
                                                                                    WalkingStep) else ""
            bus_step_polyline = segment.bus_step.polyline + ";" if isinstance(segment.bus_step, BusStep) else ""
            polyline = walking_step_polyline + bus_step_polyline
            polyline = polyline[:-1]
            # print(f'ws : {walking_step_polyline}')
            # print(f'bs : {bus_step_polyline}')
            points_str = polyline.split(";")
            for point_str in points_str:
                point = point_str.split(",")
                if len(point) == 2:
                    res.append((point[0], point[1]))
        return res

def find_last_st_in_st_set_in_route(rt: Route,st_set:list[Stop]):
    pass

def find_first_st_in_st_set_in_route(rt: Route,st_set:list[Stop]):
    pass

def parse_route_json(json_data) -> list[Route]:
    status = json_data['status']
    routes = []
    if status == '1':
        json_route = json_data['route']
        origin = json_route['origin']
        destination = json_route['destination']
        transits = json_route['transits']
        for transit in transits:
            route = Route(origin, destination, transit['distance'], transit['duration'], transit['cost'])
            segments = transit['segments']
            for segment in segments:
                ws_obj = []
                bus_obj = []
                walking = segment['walking']
                if len(walking) > 0:
                    walking_origin = walking['origin']
                    walking_destination = walking['destination']
                    walking_steps = walking['steps']
                    walking_polyline = ''
                    walking_sequence = []
                    for i, walking_step in enumerate(walking_steps):
                        walking_sequence.append(walking_step['distance'])
                        walking_polyline += walking_step['polyline'] + ';'
                    walking_polyline = walking_polyline[:-1]
                    ws_obj = WalkingStep(walking_origin, walking_destination, walking_polyline, walking['distance'],
                                        walking['duration'], walking_sequence)

                bus = segment['bus']
                if len(bus['buslines']) > 0:
                    busline = bus['buslines'][0]
                    via_stops = []
                    for vs in busline['via_stops']:
                        via_stops.append(vs['id'])
                        bus_obj = BusStep(busline['departure_stop']['id'], busline['arrival_stop']['id'], busline['id'],
                                        busline['polyline'], busline['distance'], busline['duration'], via_stops)

                route.add_segment(RouteSegment(ws_obj, bus_obj))
            routes.append(route)
    return routes


class OptimalRoutePlanningMaker:
    def make_optimal_route_plan(self, src, dst, routes, buckets_points, g):
        pass


# Trajectories must be the same length
def Euclidean_distance(route1, route2):
    pass


# Adaptation from time series distance measure
def Dynamic_time_warping(route1, route2):
    pass


# Adaptation of string similarity
# Two locations are regarded as equal if they’re ‘close’ (compared to a threshold)
def Longest_Common_Sub_Sequence(route1, route2, epsilon, sigma):
    """
    w2u = {}

    def is_the_same_point(p1, p2):
        redis_key_1 = f'lon:{p1[0]};lat:{p1[1]}'
        redis_key_2 = f'lon:{p2[0]};lat:{p2[1]}'
        p1_x, p1_y = 0, 0
        p2_x, p2_y = 0, 0
        if not rdb.exists(redis_key_1):
            p1_x, p1_y = util.transform.wgs84_to_utm(p1)
            w2u[p1] = (p1_x, p1_y)
        else:
            res = json.loads(rdb.get(redis_key_1))
            p1_x, p1_y = res['lon'], res['lat']

        if w2u.get(p2, None) is None:
            p2_x, p2_y = util.transform.wgs84_to_utm(p2)
            w2u[p2] = (p2_x, p2_y)
        else:
            p2_x, p2_y = w2u[p2]
        return abs(p1_x - p2_x) < epsilon and abs(p1_y - p2_y) < sigma
    """
    polyline1 = route1.get_polyline()
    polyline2 = route2.get_polyline()

    m = len(polyline1)
    n = len(polyline2)
    if m == 0 and n == 0:
        return 0
    if m == 0:
        return -1
    if n == 0:
        return -1
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = 1 if polyline1[0] == polyline2[0] else 0
    for i in range(1, m):
        dp[i][0] = 1 if polyline1[i] == polyline2[0] else dp[i - 1][0]
    for j in range(1, n):
        dp[0][j] = 1 if polyline1[0] == polyline2[j] else dp[0][j - 1]
    for i in range(1, m):
        for j in range(1, n):
            if polyline1[i] == polyline2[j]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m - 1][n - 1] / n


# Adaptation from Edit Distance on strings
# Threshold-based equality relationship(Like LCSS)
def Edit_Distance_On_Real_Sequence(route1, route2, epsilon):
    pass


# Used to measure how far two trajectories are from each other
def Hausdorff_Distance(route1, route2):
    pass
