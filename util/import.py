import os
import time

import database as db
from datetime import datetime

saved = 0
unsaved = 0
unsaved_list = []
'''
directory_path = './gz_trans'
for root, dirs, _ in os.walk(directory_path):
    for dir in dirs:
        dir_path = os.path.join(root, dir)
        for _, _, sub_files in os.walk(dir_path):
            for sub_file in sub_files:
                file_path = os.path.join(dir_path, sub_file)
                line_name = sub_file[:-5]
                #time.sleep(1)
                if db.get_route_stop_coordination_WGS84(line_name, "广东省广州市"):
                    saved +=1
                else:
                    unsaved += 1
                    unsaved_list.append(line_name)

'''
with open('unsaved.txt', 'r') as f:
    line = f.readline()
    while line:
        time.sleep(1)
        if db.get_route_stop_coordination_WGS84(line, "广州市"):
            saved += 1
        else:
            unsaved += 1
            unsaved_list.append(line)
        line = f.readline()


if os.path.exists('unsaved.txt'):
    os.remove('unsaved.txt')

with open('unsaved.txt', 'w') as file:
    for item in unsaved_list:
        file.write(item + '\n')

print(f"saved : {saved}, unsaved : {unsaved}, total : {saved+unsaved}")


