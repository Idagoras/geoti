from model.stop import Stop
import db.database as db
import util.transform as transform
import math
import geohash
import numpy as np


def getBucketID(st:Stop,bucket_length: int, bucket_width: int, origin_utm: tuple[float, float])-> int:
    bucket_i = math.ceil(abs(origin_utm[0] - st.x) / bucket_length) if origin_utm[0] < st.x else -math.ceil(
            abs(origin_utm[0] - st.x) / bucket_length)  
    bucket_j = math.ceil(abs(origin_utm[1] - st.y) / bucket_width) if origin_utm[1] < st.y else -math.ceil(
            abs(origin_utm[1] - st.y) / bucket_width)  
    success, bucket_id = generateBucketID(origin=origin_wgs84, m=int(bucket_length / 1000),
                n=int(bucket_width / 1000),
                i=bucket_i, j=bucket_j)
    return bucket_id

#  128 bit id: origin id (geohash 96bit) bucket width : m 6bit  bucket length: n 6bit i 10bit j 10bit
def generateBucketID(origin: tuple[float, float], m: int, n: int, i: int, j: int) -> tuple[bool, int]:
    if m > 2 ** 6 - 1 or n > 2 ** 6 - 1:
        return False, -1
    if m < 0 or n < 0:
        return False, -1
    if i < - 2 ** 9 or i > 2 ** 9 - 1 or j < - 2 ** 9 or j > 2 ** 9 - 1:
        return False, -1
    bucket_id = 0x00000000
    i = (2 ** 10 - 1) &  i
    j = (2 ** 10 - 1) &  j  
    origin_code = geohash.encode(origin[1], origin[0]).encode('utf-8')
    origin_int = int.from_bytes(origin_code, 'little') << 32
    bucket_id = bucket_id | origin_int
    bucket_id = bucket_id | (j)
    bucket_id = bucket_id | (i << 10)
    bucket_id = bucket_id | (n << 20)
    bucket_id = bucket_id | (m << 26)
    return True, int(bucket_id)


def partitionBuckets(bucket_length: int, bucket_width: int, stops: list[Stop], origin_utm: tuple[float, float],
        origin_wgs84: tuple[float, float])-> None:
    for stop in stops:
        bucket_i = math.ceil(abs(origin_utm[0] - stop.x) / bucket_length) if origin_utm[0] < stop.x else -math.ceil(
            abs(origin_utm[0] - stop.x) / bucket_length)  
        bucket_j = math.ceil(abs(origin_utm[1] - stop.y) / bucket_width) if origin_utm[1] < stop.y else -math.ceil(
            abs(origin_utm[1] - stop.y) / bucket_width)  
        success, bucket_id = generateBucketID(origin=origin_wgs84, m=int(bucket_length / 1000),
                n=int(bucket_width / 1000),
                i=bucket_i, j=bucket_j)
        print(f"{bucket_i},{bucket_j},{bucket_id}")
        if success:
            if not db.bucket_exist(bucket_id=bucket_id):
                db.insert_bucket(bucket_id=bucket_id)
            if not db.stop_is_in_bucket(bucket_id=bucket_i, stop_id=stop.stop_id):
                line_ids_res = db.query_all_lines_pass_through(stop.stop_id)
                line_ids = [line_id_res[0] for line_id_res in line_ids_res]
                db.update_bucket_s_stops_and_lines(bucket_id=bucket_id, stop_id=stop.stop_id, line_ids=line_ids)


origin_wgs84 = (113.264499, 23.130061)  # origin under wgs84 of guangzhou
origin_utm = transform.wgs84_to_utm(origin_wgs84)  # origin under utm of guangzhou

def get_stop(stop_id:str)->Stop | None:
    exist, st = db.query_stop(stop_id=stop_id)
    if exist and st is not None:
    return Stop(pos=(st.latitude,st.longitude),stop_id=stop_id) # type: ignore

def get_set_of_stops_with_direct_connection(stop_id: str)-> list[Stop] | None:
    sts = db.query_all_stops_nearby(stop_id=stop_id,x=1)
    res = []
    for st in sts:
        st_id = st[1]
        res.append(get_stop(stop_id=st_id))
    return res

def update_route_info(dest_id: str,start_id: str, info: dict[str,str], two_way: bool)-> None:
    s2d_info = dict(info)
    s2d_info["start"] = start_id
    s2d_info["end"] = dest_id
    db.update_or_insert_route_info(route_info=s2d_info)
    if two_way:
        d2s_info = dict(info)
        d2s_info["start"] = dest_id
        d2s_info["end"] = start_id
        db.update_or_insert_route_info(route_info=d2s_info)

def get_route_info(dest_id: str,start_id: str)-> dict:
    route_info = {}
    exist, res = db.query_route_info(st_id=start_id,end_id=dest_id)
    res = res[0]
    route_info["start"] = res[0]
    route_info["end"] = res[1]
    route_info["distance_euclid"] = res[2]
    route_info["distance_sp"] = res[3]
    route_info["cost"] = res[4]
    route_info["duration"] = res[5]
    route_info["polyline"] = res[6]
    route_info["via_stops"] = res[7]
    route_info["via_lines"] = res[8]
    return route_info
    
def get_bucket_info(bucket_id: int)-> tuple[bool,dict]:
    res = db.query_bucket_info(bucket_id=bucket_id)
    bucket_info = {}
    bucket_info[""]
    
    return True,bucket_info

def get_distances_to_stops(origin:Stop,sts: list[Stop])-> list[list[int]]:
    res = []
    for st in sts:
        route_info = get_route_info(start_id=origin.stop_id,dest_id=st.stop_id)
        res.append([route_info["distance_euclid"],route_info["distance_sp"]])
    return res
        
if __name__ == '__main__':
    stops_res = db.all_stops()
    stops = [Stop((st[2], st[3]), st[0]) for st in stops_res]
    partitionBuckets(bucket_length=1000, bucket_width=1000, stops=stops, origin_utm=origin_utm,
            origin_wgs84=origin_wgs84)
