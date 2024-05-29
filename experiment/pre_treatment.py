from db.store import Store
from model.stop import Stop
import db.store as ds
import numpy as np
from lbs import LBSServer
import networkx as nx 

MAX_COST = 10000
MAX_TIME = 10000
MAX_DISTANCE = 100000


def prepare_buckets_of_pair(start_to_end_pair: tuple[Stop, Stop], store: Store, server: LBSServer) -> dict[str,list|dict]:
    start_stop = start_to_end_pair[0]
    end_stop = start_to_end_pair[1]
    city_name = start_stop.city_name
    start_stop_bucket_i, start_stop_bucket_j = start_stop.bucket_pos(ds.ORIGIN_XY, ds.BUCKET_M, ds.BUCKET_N)
    points_in_start_bucket = store.points_in_same_bucket(city_name, ds.BUCKET_M, ds.BUCKET_N,(start_stop.stop_id, start_stop.longitude,start_stop.latitude))
    end_stop_bucket_i, end_stop_bucket_j = end_stop.bucket_pos(ds.ORIGIN_XY, ds.BUCKET_M, ds.BUCKET_N)
    points_in_end_bucket = store.points_in_same_bucket(city_name, ds.BUCKET_M, ds.BUCKET_N,(end_stop.stop_id, end_stop.longitude, end_stop.latitude))
    # start_point
    start_stops_to_index = {}
    i = 0
    for point in points_in_start_bucket:
        start_stops_to_index[point[0]] = i
        i += 1
    start_lines_matrix = get_lines_matrix_of_bucket(points_in_start_bucket, start_stops_to_index, store, city_name,server)

    # end_point
    end_stops_to_index = {}
    i = 0
    for point in points_in_end_bucket:
        end_stops_to_index[point[0]] = i
        i += 1
    end_lines_matrix = get_lines_matrix_of_bucket(points_in_end_bucket, end_stops_to_index, store, city_name, server)


def get_lines_matrix_of_bucket(points_in_bucket, stops_to_index, store: Store, city_name: str,server: LBSServer) -> dict:
    lines_matrix = {}
    for point in points_in_bucket:
        lines = store.line_pass_through(city_name, point[0])
        for line in lines:
            start_stop_id = point[0]
            stops_line_linked = store.around_stops_by_stops_num(stop_id=start_stop_id, stop_num=1, line_id=line)
            for next_stop in stops_line_linked:
                next_stop_id = next_stop[1]
                if next_stop_id in stops_to_index:
                    next_stop_info = store.stop_by_id(next_stop_id, city_name)
                    next_stop_pos = (next_stop_info["longitude"], next_stop_info["latitude"])
                    start_stop_pos = point[2]
                    _, res_cost_distance_duration_list = server.querySpecificLineAndReturnDistanceAndCost(
                        start_stop_pos,
                        next_stop_pos,
                        city_name, line)
                    print(res_cost_distance_duration_list)
                    if line not in lines_matrix:
                        lines_matrix[line] = {
                            'cost': np.full([len(stops_to_index), len(stops_to_index)], fill_value=MAX_COST, dtype=int),
                            'distance': np.full([len(stops_to_index), len(stops_to_index)],fill_value=MAX_DISTANCE, dtype=int),
                            'duration': np.full([len(stops_to_index), len(stops_to_index)],fill_value=MAX_TIME, dtype=int)
                        }
                    line_matrix = lines_matrix[line]
                    start_stop_index = stops_to_index[start_stop_id]
                    next_stop_index = stops_to_index[next_stop_id]
                    line_matrix['cost'][start_stop_index][next_stop_index] = int(res_cost_distance_duration_list[0])
                    line_matrix['distance'][start_stop_index][next_stop_index] = int(res_cost_distance_duration_list[1])
                    line_matrix['duration'][start_stop_index][next_stop_index] = int(res_cost_distance_duration_list[2])

    return lines_matrix


def generateDirectDistanceMatrix(lines_distance_matrix: np.array) -> np.array:
    pass


def generateTotalDirectDistanceMatrix():
    pass


def generateDirectFareMatrix():
    pass


def generateShortestTimeMatrix():
    pass


def generateDirectRelationshipMatrix():
    pass
