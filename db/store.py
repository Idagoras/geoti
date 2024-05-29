import json
import math
import util.transform as transform
import redis
import db.database
import model.stop

REDIS_STOPS_SET_KEY = ":transportation_stops:set"
REDIS_STOPS_GEO_KEY = ":transportation_stops:geo"
REDIS_STOPS_HASH_KEY = ":transportation_stops:hash"
REDIS_STOP_LINE_KEY = ":transportation_stop:line:"
REDIS_STOP_NUM_ZSET_KEY = ":transportation_stops:num:zset"
REDIS_STOP_NUM_HASH_KEY = ":transportation_stops:num:hash"
REDIS_LINES_HASH_KEY = ":transportation_lines:hash"
REDIS_LBS_QUERY_HASH_KEY = ":transportation_query:hash"
REDIS_BUCKET_GEO_KEY = ":transportation_bucket:geo:"
REDIS_BUCKET_COUNT_ZSET_KEY = ":transportation_bucket:count:"
REDIS_BUCKET_INFO_KEY = ":transportation_bucket:info:"
ORIGIN = (113.264499, 23.130061)
ORIGIN_XY = transform.wgs84_to_utm(ORIGIN)
BUCKET_M = 2000
BUCKET_N = 2000


class Store(object):
    def __init__(self, city_list):
        self.redisClient = redis.Redis(host='localhost', port=6379, db=0)
        """
        for city in city_list:
            city_name = city.lower()
            city_redis_set_key = city_name + REDIS_STOPS_SET_KEY
            city_redis_geo_key = city_name + REDIS_STOPS_GEO_KEY
            city_redis_hash_key = city_name + REDIS_STOPS_HASH_KEY
            city_redis_stop_num_hash_key = city_name + ":" + REDIS_STOP_NUM_HASH_KEY
            exist = self.redisClient.exists(city_redis_set_key) and self.redisClient.exists(
                city_redis_geo_key)
            if not exist:
                stops = db.database.all_stops()
                for stop in stops:
                    # print(stop)
                    self.redisClient.sadd(city_redis_set_key, stop[0])
                    self.redisClient.geoadd(city_redis_geo_key, [stop[2], stop[3], stop[0]])
                    self.redisClient.hmset(city_redis_hash_key + stop[0], {
                        "id": stop[0],
                        "stop_name": stop[1],
                        "longitude": stop[2],
                        "latitude": stop[3],
                        "line_id_to_sequence": json.dumps(stop[4])
                    })
                    self.redisClient.hset(city_redis_stop_num_hash_key, city_redis_stop_num_hash_key, 0)
            city_bucket_num_redis_key = city_name + REDIS_BUCKET_COUNT_ZSET_KEY + f":{BUCKET_M},{BUCKET_N}"
            if not self.redisClient.exists(city_bucket_num_redis_key):
                stops = db.database.all_stops()
                for stop in stops:
                    self.add_point_to_bucket(city_name, (stop[0], stop[2], stop[3]), BUCKET_M, BUCKET_N)
            """

    def random_stops_pair(self, city_name):
        city_redis_set_key = city_name + REDIS_STOPS_SET_KEY
        stops_pair = self.redisClient.srandmember(city_redis_set_key, 2)
        return stops_pair

    # @output:map:{
    #
    #
    # }
    def stop_by_id(self, stop_id, city_name):
        city_redis_hash_key = city_name + REDIS_STOPS_HASH_KEY + stop_id
        if self.redisClient.exists(city_redis_hash_key):
            stop = self.redisClient.hgetall(city_redis_hash_key)
            res = {
                "id": stop[b"id"].decode("utf-8"),
                "latitude": float(stop[b"latitude"].decode("utf-8")),
                "longitude": float(stop[b"longitude"].decode("utf-8")),
                "stop_name": stop[b"stop_name"].decode("utf-8"),
                "line_id_to_sequence": stop[b"line_id_to_sequence"].decode("utf-8")
            }
            return res
        else:
            ex, stop = db.database.query_stop(stop_id)
            if not ex:
                return {}
            else:
                return stop

    def around_stops_by_distance(self, city_name, stop_id, distance):
        city_redis_geo_key = city_name + REDIS_STOPS_GEO_KEY
        return self.redisClient.georadiusbymember(city_redis_geo_key, stop_id, distance, "km", withcoord=True)

    def around_stops_by_stops_num(self, stop_id, stop_num, line_id):
        stops = db.database.query_all_stops_nearby(stop_id, stop_num)
        res = []
        for stop in stops:
            if stop[2] == line_id :
                res.append(stop)
        return res

    def line_pass_through(self, city_name, stop_id):
        lines = db.database.query_all_lines_pass_through(stop_id)
        res = []
        for line in lines:
            res.append(line[0])
        return res

    def line_by_id(self, city_name, line_id):
        city_redis_line_hash_key = city_name + REDIS_LINES_HASH_KEY + line_id
        if self.redisClient.exists(city_redis_line_hash_key):
            return self.redisClient.hgetall(city_redis_line_hash_key)
        else:
            line = db.database.query_line(line_id)
            line_map = {
                "id": line.id,
                "line_name": line.line_name,
                "vehicle_type": line.vehicle_type,
                "stop_num": line.stop_num,
                "start_time": line.start_time,
                "end_time": line.end_time,
                "polyline": line.polyline,
                "basic_price": line.basic_price,
                "total_price": line.total_price,
                "direc": line.direc
            }
            self.redisClient.hmset(city_redis_line_hash_key, line_map)
            return line_map

    def lbs_query(self, city_name, src_stop_id, dst_stop_id):
        city_redis_lbs_query_hash_key = city_name + ":" + src_stop_id + ":" + dst_stop_id + REDIS_LBS_QUERY_HASH_KEY
        if self.redisClient.exists(city_redis_lbs_query_hash_key):
            return self.redisClient.hgetall(city_redis_lbs_query_hash_key)
        else:
            return None

    def save_lbs_query(self, city_name, src_stop_id, dst_stop_id, lbs_query):
        city_redis_lbs_query_hash_key = city_name + ":" + src_stop_id + ":" + dst_stop_id + REDIS_LBS_QUERY_HASH_KEY
        self.redisClient.hmset(city_redis_lbs_query_hash_key, lbs_query)

    def stops(self, city_name):
        city_redis_stops_set_key = city_name + REDIS_STOPS_SET_KEY
        city_redis_stops_geo_key = city_name + REDIS_STOPS_GEO_KEY
        stop_ids = self.redisClient.smembers(city_redis_stops_set_key)
        res = self.redisClient.georadius(city_redis_stops_geo_key, ORIGIN[0], ORIGIN[1], 10000, 'km', withcoord=True)
        return res

    def add_point_to_bucket(self, city_name, point, m, n):
        origin_x, origin_y = transform.wgs84_to_utm(ORIGIN)
        point_x, point_y = transform.wgs84_to_utm((point[1], point[2]))
        bucket_i = math.ceil(float(point_x - origin_x) / n)
        bucket_j = math.ceil(float(point_y - origin_y) / m)
        # print(f"{bucket_i},{bucket_j}\n")
        city_bucket_ij_redis_key = city_name + REDIS_BUCKET_GEO_KEY + f":({m},{n}):({bucket_i},{bucket_j})"
        self.redisClient.geoadd(city_bucket_ij_redis_key, [point[1], point[2], point[0]])
        city_bucket_count_key = city_name + REDIS_BUCKET_COUNT_ZSET_KEY + f":count:({m},{n})"
        city_bucket_ij_count_redis_key = city_name + REDIS_BUCKET_GEO_KEY + f":({m},{n}):({bucket_i},{bucket_j})"
        self.redisClient.zincrby(city_bucket_count_key, 1, city_bucket_ij_count_redis_key)

    # @output: list:[list:[bytes:stop_id, float:distance, tuple(float,float):(longitude,latitude)]]
    def points_in_same_bucket(self, city_name, m, n, point):
        origin_x, origin_y = transform.wgs84_to_utm(ORIGIN)
        point_x, point_y = transform.wgs84_to_utm((point[1], point[2]))
        bucket_i = math.ceil(float(point_x - origin_x) / n)
        bucket_j = math.ceil(float(point_y - origin_y) / m)
        city_bucket_ij_redis_key = city_name + REDIS_BUCKET_GEO_KEY + f":({m},{n}):({bucket_i},{bucket_j})"
        members = self.redisClient.georadius(city_bucket_ij_redis_key, point[1], point[2], 10, 'km', withdist=True,
                                            withcoord=True)
        return [[member[0].decode('utf-8'), member[1], member[2]] for member in members]

    def add_virtual_node_to_bucket(self, bucket_id, stop_id):
        virtual_node_redis_key = f"transportation:virtual-node-{stop_id}-{bucket_id}:set"
        self.redisClient.sadd(virtual_node_redis_key, bucket_id)

    # @output: list:[list:[bytes:stop_id,tuple(float,float):(longitude,latitude)]]
    def points_in_bucket(self, city_name, m, n, i, j, longitude, latitude):
        city_bucket_ij_redis_key = city_name + REDIS_BUCKET_GEO_KEY + f":({m},{n}):({i},{j})"
        points = self.redisClient.georadius(city_bucket_ij_redis_key, longitude, latitude,
                                            math.sqrt(math.pow(m, 2) + math.pow(n, 2)) / 2, 'km', withcoord=True)
        for point in points:
            point[0] = point[0].decode('utf-8')
        return points

    # @output: 2-d list: [map:{bytes:key:float/bytes:value}]
    # @key-value: "distance":flaot(unit:km)
    def bucket_info(self, city_name, m, n, i, j, longitude, latitude):
        def distance(p1, p2):
            p1_x, p1_y = transform.wgs84_to_utm(p1[1])
            p2_x, p2_y = transform.wgs84_to_utm(p2[1])
            return round(math.sqrt(math.pow(p1_x - p2_x, 2) + math.pow(p1_y - p2_y, 2)) / 1000, 3)

        city_bucket_info_redis_key = city_name + REDIS_BUCKET_INFO_KEY + f":({m},{n}):({i},{j})"
        if self.redisClient.exists(city_bucket_info_redis_key):
            info_str = self.redisClient.get(city_bucket_info_redis_key)
            return json.loads(info_str)

        points = self.points_in_bucket(city_name, m, n, i, j, longitude, latitude)
        l = len(points)
        info = [[{} for _ in range(l)] for _ in range(l)]
        points_id = [points[i][0] for i in range(l)]
        for point in points:
            around_stops = self.around_stops_by_stops_num(city_name, point[0], 1)
            for around_stop in around_stops:
                if around_stop in points_id:
                    info[points.index(point)][points_id.index(around_stop)] = {
                        'distance': distance(point, points[points_id.index(around_stop)])}
        self.redisClient.set(city_bucket_info_redis_key, json.dumps(info))
        return info

    def next_stop(self, start_id, line_id):
        res = db.database.query_stops_with_start_id_and_line_id(start_id, line_id)
        return res


"""
store = Store(["guangzhou"])
s = point.Stop((113.29286, 23.092125),"BV11594764")
i, j = s.bucket_pos(transform.wgs84_to_utm(ORIGIN), BUCKET_M, BUCKET_N)

print(store.points_in_bucket("guangzhou", BUCKET_M, BUCKET_N, i, j, s.longitude, s.latitude))
info = store.bucket_info('guangzhou', BUCKET_M, BUCKET_N, i, j, s.longitude, s.latitude)
for i in range(len(info)):
    for j in range(len(info[0])):
        print(info[i][j])
"""
