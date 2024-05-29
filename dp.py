import csv
import string
import time

from db.store import Store
import db.store as dbs
from lbs import LBSServer
from point import Stop
import networkx as nx
import perturbation as pb
import route
import matplotlib.pyplot as plt


class QueryResult:
    def __init__(self, start_id, end_id, similarity, k, m, n, epsilon, duration):
        self.start_id = start_id
        self.end_id = end_id
        self.similarity = similarity
        self.k = k
        self.m = m
        self.n = n
        self.epsilon = epsilon
        self.duration = duration


def saveQueryResultSetToCSV(query_result_set, file_name):
    total = len(query_result_set)
    index = 0
    with open(file_name + ".csv", 'w') as file:
        while index < total:
            data = [index, query_result_set[index].start_id, query_result_set[index].end_id,
                    query_result_set[index].similarity,
                    query_result_set[index].k, query_result_set[index].m, query_result_set[index].n,
                    query_result_set[index].epsilon,
                    query_result_set[index].duration]
            writer = csv.writer(file)
            writer.writerow(data)
            index += 1


def infoToGraph(info, nodes):
    g = nx.DiGraph()
    for node in nodes:
        g.add_node(node[0])
    m = len(info)
    for i in range(m):
        for j in range(m):
            if info[i][j] != {}:
                g.add_edge(nodes[i][0], nodes[j][0], distance=info[i][j]['distance'])
    return g


def getK(g):
    return len(list(nx.strongly_connected_components(g)))


class Requestor:
    def __init__(self, store, lbs_server):
        self.store: Store = store
        self.lbs = lbs_server

    # 从 csv 文件读取一组待查询的起点终点对
    # 指定 bucket 的长 m ，宽 n，查询次数 k
    # 返回
    def queryFromCSVFile(self, filename, city_name, m, n, saved):
        result_set = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                start_id = row[1]
                end_id = row[2]
                res = self.query(start_id, end_id, city_name, m, n)
                result_set.append(res)
        saveQueryResultSetToCSV(result_set, f"result/{saved}")
        return result_set

    def query(self, start, destination, city_name: string, m, n):
        st_time = time.time()
        start_stop_dict = self.store.stop_by_id(start, city_name)
        # print(start_stop_dict)
        destination_stop_dict = self.store.stop_by_id(destination, city_name)
        start_stop = Stop((start_stop_dict["longitude"], start_stop_dict["latitude"]), start)
        destination_stop = Stop((destination_stop_dict["longitude"], destination_stop_dict["latitude"]), destination)
        actual_success, actual_route = self.lbs.query(start_stop.pos(), destination_stop.pos(), city_name)
        start_bucket_nodes = self.store.points_in_same_bucket(city_name, m, n, start_stop.point())
        start_bucket_info = self.store.bucket_info(city_name, m, n, start_stop.bucket_pos(dbs.ORIGIN_XY, m, n)[0],
                                                   start_stop.bucket_pos(dbs.ORIGIN_XY, m, n)[1], start_stop.longitude,
                                                   start_stop.latitude)
        destination_bucket_nodes = self.store.points_in_same_bucket(city_name, m, n, destination_stop.point())
        destination_bucket_info = self.store.bucket_info(city_name, m, n,
                                                         destination_stop.bucket_pos(dbs.ORIGIN_XY, m, n)[0],
                                                         destination_stop.bucket_pos(dbs.ORIGIN_XY, m, n)[1],
                                                         destination_stop.longitude,
                                                         destination_stop.latitude)
        st_g = infoToGraph(start_bucket_info, start_bucket_nodes)
        dest_g = infoToGraph(destination_bucket_info, destination_bucket_nodes)

        st_k = getK(st_g)
        dest_g = getK(dest_g)
        print(f"st_k = {st_k}, dest_g = {dest_g}")
        dp_start = pb.perturbByExponentialMechanismWithGraph(start_bucket_nodes)
        dp_dest = pb.perturbByExponentialMechanismWithGraph(destination_bucket_nodes)
        print(f"actual start:{start},actual destination:{destination},dp start:{dp_start},dp destination:{dp_dest}")

        dp_start_dict = self.store.stop_by_id(dp_start, city_name)
        dp_destination_dict = self.store.stop_by_id(dp_dest, city_name)
        dp_start_stop = Stop((dp_start_dict['longitude'], dp_start_dict['latitude']), dp_start)
        dp_destination_stop = Stop((dp_destination_dict['longitude'], dp_destination_dict['latitude']), dp_dest)
        dp_success, dp_route = self.lbs.query(dp_start_stop.pos(), dp_destination_stop.pos(), city_name)
        # print(actual_route)
        # print(dp_route)
        ed_time = time.time()
        if actual_success and dp_success:
            similarity = route.Longest_Common_Sub_Sequence(actual_route, dp_route, 0.01, 0.01)
        else:
            similarity = -1
        result: QueryResult = QueryResult(start, destination, similarity, 1, m, n, pb.EPSILON, ed_time - st_time)
        return result


lbs_server = LBSServer("3bf4992397329e61be6b62a1399a2145")
store = Store(['guangzhou'])
req = Requestor(store, lbs_server)
req.queryFromCSVFile("sources/guangzhou_ds_03.csv", "guangzhou", 2000, 2000, "result_ds_03")
