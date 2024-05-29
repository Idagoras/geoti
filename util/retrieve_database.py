import os
import time

import database as db
import json

saved = 0
unsaved = 0
unsaved_list = []
unsaved_stops = []
'''
directory_path = './gz_trans'
for root, dirs, _ in os.walk(directory_path):
    for dr in dirs:
        dir_path = os.path.join(root, dr)
        for _, _, sub_files in os.walk(dir_path):
            for sub_file in sub_files:
                file_path = os.path.join(dir_path, sub_file)
                line_name = sub_file[:-5]
                if db.get_route_stop_coordination_WGS84(line_name, "广东省广州市", False):
                    saved += 1
                else:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        first_stop = data[0][0][2:]
                        unsaved_stops.append(first_stop)
                    unsaved += 1
                    unsaved_list.append(line_name)


if os.path.exists('unsaved.txt'):
    os.remove('unsaved.txt')
'''
if os.path.exists('unsaved_stops.txt'):
    os.remove('unsaved_stops.txt')

with open('unsaved.txt', 'r') as file:
    data = json.load(file)
    first_stop = data[0][0][2:]
    unsaved_stops.append(first_stop)

#with open('unsaved.txt', 'w') as file:
 #   for item in unsaved_list:
  #      file.write(item + '\n')

with open('unsaved_stops.txt', 'w') as file:
    for item in unsaved_stops:
        file.write(item + '\n')

print(f"saved : {saved}, unsaved : {unsaved}, total : {saved + unsaved}")

'''
unsaved_line_ids = []

with open('unsaved_stops.txt', 'r') as file:
    line = file.readline()
    while line:
        res = db.get_line_id_by_stop_name(line,'广州市')
        unsaved_line_ids.extend(res)
        time.sleep(1)
        line = file.readline()

if os.path.exists('unsaved_line_id.txt'):
    os.remove('unsaved_line_id.txt')

with open('unsaved_line_id.txt', 'w') as file:
    for item in unsaved_line_ids:
        file.write(item + '\n')
        
'''