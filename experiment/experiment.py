import dataset_reader
import pre_treatment
from db.store import Store
from lbs import LBSServer
import numpy as np

if __name__ == '__main__':
    store = Store(["guangzhou"])
    server = LBSServer("3bf4992397329e61be6b62a1399a2145")
    stop_pairs_list = dataset_reader.read('../sources/guangzhou_ds_04.csv', 1)
    for stop_pair in stop_pairs_list:
        ret = pre_treatment.prepare_buckets_of_pair(stop_pair, store, server)
