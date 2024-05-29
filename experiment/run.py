import csv
import db.gzstore as store
import networkx as nx
import json
import perturbation as pb
from model.stop import Stop
from route import Route
from lbs import LBSServer

m = 2000
n = 2000
k = 5
epsilon = 0.1
server = LBSServer()
city_name = "guangzhou"

def read(csv_file_path: str,max_read_rows:int) -> (list[tuple[Stop, Stop]]):
    stop_tuple_list: list[tuple[Stop, Stop]] = []
    with open(csv_file_path, 'r') as f:
        reader = csv.reader(f)
        i = 0
        for row in reader:
            if i >= max_read_rows:
                break
            start_id: str = row[1]
            end_id: str = row[2]
            start_stop = store.get_stop(stop_id=start_id)
            end_stop = store.get_stop(stop_id=end_id)
            if start_stop is not None and end_stop is not None:
                stop_tuple_list.append((start_stop, end_stop))
    return stop_tuple_list

def load_bucket(bucket_id:int)->dict:
    exist, bucket_info = store.get_bucket_info(bucket_id=bucket_id)
    ret = {}
    if exist:
        if 'shortest_time' in bucket_info:
            data = bucket_info['shortest_time']
            json_data = json.loads(data)
            g = nx.node_link_graph(json_data)
            ret = bucket_info.copy()
        else:
            g = nx.DiGraph()
            sts = bucket_info['stops']
            for i in range(len(sts)):
                g.add_node(i)
            for i in range(len(sts)):                
                for j in range(i,len(sts)):
                    if i == j:
                        g.add_edge(i,j,distance_e=0,duration=0)
        return ret    
    else:
        return  {}

def compute_optimal_route(start:Stop,end:Stop)->Route:
    start_bucket = load_bucket(store.getBucketID(st=start,bucket_length=m,bucket_width=n,origin_utm=store.origin_utm))
    end_bucket = load_bucket(store.getBucketID(st=end,bucket_length=m,bucket_width=n,origin_utm=store.origin_utm))
    st_distances_list = store.get_distances_to_stops(start,start_bucket["stops"]) 
    ed_distances_list = store.get_distances_to_stops(end,end_bucket["stops"])
    st_costs = [st_distance_list[0] for st_distance_list in st_distances_list]
    ed_costs = [ed_distance_list[0] for ed_distance_list in ed_distances_list]
    st_ids = [st.stop_id() for st in start_bucket["stops"]]
    ed_ids = [ed.stop_id() for ed in end_bucket["stops"]]
    for _  in range(k):
        pb_start: Stop = pb.perturbByExponentialMechanism(start_bucket["stops"],costs=st_costs,epsilon=epsilon)
        pb_end: Stop = pb.perturbByExponentialMechanism(end_bucket["stops"],costs=ed_costs,epsilon=epsilon)
        success, pb_route = server.query(start=pb_start.pos(),destination=pb_end.pos(),city_name=city_name)
        if success:
            last_st_in_st_bucket = []
            