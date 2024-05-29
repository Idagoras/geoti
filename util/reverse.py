import os

with open('unsaved_conghua.txt', 'r') as file:
    lines = file.readlines()

os.remove('unsaved_conghua.txt')
lines.reverse()

with open('unsaved_conghua.txt', 'w') as file:
    file.writelines(lines)