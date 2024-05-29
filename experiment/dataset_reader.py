import csv
import db.gzstore as store
from model.stop import Stop


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

