import time

import database as db

saved = 0
unsaved = 0
messages = []

with open('unsaved.txt', 'r') as file:
    line = file.readline()
    while line:
        is_saved, message = db.get_line_by_line_id(line[:-1])
        if is_saved:
            saved += 1
        else:
            unsaved += 1
        messages.append(message)
        time.sleep(0.5)
        line = file.readline()
print(f'saved {saved}, unsaved {unsaved}')

with open('messages.txt', 'w') as file:
    for message in messages:
        file.write(message + '\n')
