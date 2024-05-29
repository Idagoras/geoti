import csv

import db.store


def generateDataSetCsvFile(store:db.store.Store,city_name,file_name,count):
    total = count
    with open(file_name+".csv",'w') as file:
        while count > 0:
            stop_pairs = store.random_stops_pair("guangzhou")
            src = stop_pairs[0].decode('utf-8')
            dst = stop_pairs[1].decode('utf-8')
            if src == dst:
                continue
            index = total - count + 1
            data = [index,src,dst]
            writer = csv.writer(file)
            writer.writerow(data)
            count -= 1


store = db.store.Store(["guangzhou"])
generateDataSetCsvFile(store,"guangzhou","../sources/guangzhou_ds_01",10000)