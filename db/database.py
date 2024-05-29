from typing import Sequence
from sqlalchemy import create_engine, exc, or_, text, cast, Numeric, select, and_, desc, func
from sqlalchemy.orm import sessionmaker, aliased
from datetime import datetime
import requests
import json
import re
import model.model as db_model

BAIDU_AK = 'o5T0DcUIKlQZ4pj5Ngz6g4PIcxwxylfX'
GAODE_AK = '3bf4992397329e61be6b62a1399a2145'
GAODE_1_AK = '966b2f7ba835f96c84b909279b112588'
GAODE_2_AK = '39884b28c6fbf518b2c486b60121fb38'
DATABASE_URL = 'postgresql://idagoras:314159@localhost:5432/shiftroute'
SUGGESTIONS_URL = 'https://api.map.baidu.com/place/v2/suggestion'
TREANSPORT_QUERY_URL = 'https://restapi.amap.com/v3/bus/linename'
STOP_QUERY_URL = 'https://restapi.amap.com/v3/bus/stopname'
LINE_ID_QUERY_URL = 'https://restapi.amap.com/v3/bus/lineid'
VEHICLE_TABLE_NAME = ''
STOP_TABLE_NAME = ''

engine = create_engine(DATABASE_URL, echo=True)

# db_model.Stop.__tablename__ = STOP_TABLE_NAME
# db_model.Vehicle.__tablename__ = VEHICLE_TABLE_NAME

Base = db_model.Base

Base.metadata.create_all(engine, checkfirst=True)

Session = sessionmaker(bind=engine)


def insert_vehicle(line_id, line_name, stop_num, start_time, end_time, vehicle_type, polyline, basic_price, total_price,
                direc):
    try:
        session = Session()
        new_vehicle = db_model.Vehicle(line_id, line_name, db_model.VehicleType(vehicle_type), stop_num, start_time,
                                    end_time, polyline, basic_price, total_price, direc)
        session.add(new_vehicle)
        session.commit()
        session.close()
    except exc.SQLAlchemyError as e:
        print(e)
        session.rollback()
        print('add vehicle name: {name} failed')
    finally:
        session.close()


def query_stop(stop_id):
    session = Session()
    query = session.query(db_model.Stop).filter(db_model.Stop.id == stop_id)
    result = query.all()
    session.close()
    if len(result) == 0:
        return False, None
    else:
        stop = result[0]
        return True, stop


def query_line(line_id):
    session = Session()
    query = session.query(db_model.Vehicle).filter(db_model.Vehicle.id == line_id)
    result = query.all()
    print(len(result))
    session.close()
    if len(result) == 0:
        return False, None
    else:
        line = result[0]
        return True, line


def query_line_with_similar_name(line_name):
    query = []
    session = Session()
    name_condition_1 = db_model.Vehicle.line_name.like('%' + line_name + '%')
    if '南沙' in line_name:
        new_line_name = line_name.replace('南沙', '南')
        name_condition_2 = db_model.Vehicle.line_name.like('%' + new_line_name + '%')
        combined_condition = or_(name_condition_1, name_condition_2)
        query = session.query(db_model.Vehicle).filter(combined_condition)
    else:
        query = session.query(db_model.Vehicle).filter(name_condition_1)
    result = query.all()
    session.close()
    if len(result) == 0:
        return False, None
    else:
        return True, result


def insert_stop(stop_id, location, stop_name, sequence, line_id):
    try:
        session = Session()
        location_sp = location.split(',')
        record = session.query(db_model.Stop).filter(db_model.Stop.id == stop_id).first()
        if record:
            current_json = record.line_id_to_sequence
            l2s = json.loads(current_json)
            l2s[line_id] = sequence
            record.line_id_to_sequence = l2s
            session.commit()
        else:
            new_stop = db_model.Stop(stop_id, line_id, stop_name, location_sp[0], location_sp[1], sequence)
            session.add(new_stop)
            session.commit()
        session.close()
    except Exception as e:
        print(e)
        session.rollback()
        print(f'insert stop name :{stop_name} failed')
    finally:
        session.close()


exhausted = False
cur_ak_index = 1
aks = [GAODE_AK, GAODE_1_AK, GAODE_2_AK]


def get_route_stop_coordination_WGS84(line_name, city_name, query_api=True) -> bool:
    line_saved, _ = query_line_with_similar_name(line_name)
    if line_saved:
        print(f'line saved: {line_saved}')
        return True
    else:
        print(f'line not saved: {line_name}')
        if not query_api:
            return False
    params = {"key": aks[cur_ak_index], "keywords": line_name, "city": city_name, "output": "JSON",
            "extensions": "all"}
    response = requests.get(TREANSPORT_QUERY_URL, params=params)
    data = response.json()
    if response.status_code == 200:
        if data['status'] == '1':
            buslines = data['buslines']
            for busline in buslines:
                line_id = busline['id']
                line_exist, _ = query_line(line_id)
                if not line_exist:
                    name = busline['name']
                    basic_price = busline['basic_price']
                    total_price = busline['total_price']
                    polyline = busline['polyline']
                    start_time = busline['start_time']
                    end_time = busline['end_time']
                    print(start_time)
                    print(end_time)
                    st = datetime.utcnow()
                    et = datetime.utcnow()
                    # if isinstance(start_time, str):
                    #   st = datetime.strptime(start_time, "%H%M").time()
                    # if isinstance(end_time, str):
                    #   et = datetime.strptime(end_time, "%H%M").time()
                    direc = busline['direc']
                    busstops = busline['busstops']
                    insert_vehicle(line_id, name, len(busstops), st, et, 0, polyline, basic_price, total_price, direc)
                    for stop in busstops:
                        stop_id = stop['id']
                        location = stop['location']
                        stop_name = stop['name']
                        sequence = stop['sequence']
                        insert_stop(stop_id, location, stop_name, sequence, line_id)

            return True
        else:
            print(data)
            return False
    else:
        print(data)
        return False


def get_line_id_by_stop_name(stop_name, city_name):
    result = []
    param = {'key': aks[cur_ak_index], 'keywords': stop_name, 'city': city_name}
    response = requests.get(STOP_QUERY_URL, params=param)
    data = response.json()
    if data['status'] == '1':
        print(data['count'])
        for stop in data['busstops']:
            buslines = stop['buslines']
            for busline in buslines:
                result.append(busline['id'])
    else:
        print(data)
    return result


def get_line_by_line_id(line_id):
    line_exist, _ = query_line(line_id)
    if not line_exist:
        param = {'key': aks[cur_ak_index], 'id': line_id, 'extensions': 'all'}
        response = requests.get(LINE_ID_QUERY_URL, params=param)
        data = response.json()
        if data['status'] == '1':
            buslines = data['buslines']
            for busline in buslines:
                name = busline['name']
                basic_price = busline['basic_price']
                total_price = busline['total_price']
                polyline = busline['polyline']
                start_time = busline['start_time']
                end_time = busline['end_time']
                print(start_time)
                print(end_time)
                st = datetime.utcnow()
                et = datetime.utcnow()
                direc = busline['direc']
                busstops = busline['busstops']
                insert_vehicle(line_id, name, len(busstops), st, et, 0, polyline, basic_price, total_price, direc)
                for stop in busstops:
                    stop_id = stop['id']
                    location = stop['location']
                    stop_name = stop['name']
                    sequence = stop['sequence']
                    insert_stop(stop_id, location, stop_name, sequence, line_id)
            return True, ''
        else:
            print(data)
            return False, f'query line with error:{line_id}'
    else:
        print('line exist in database')
        return False, f'line exist in database : {line_id}'


def get_stops_around(stop_id, radius_small, radius_large, lat=-1000, lon=-1000):
    try:
        session = Session()
        if lat == -1000 and lon == -1000:
            stop_record = session.query(db_model.Stop.latitude, db_model.Stop.longitude).filter(
                db_model.Stop.id == stop_id).all()
            if len(stop_record) == 0:
                print(f'no stop found : stop id {stop_id}')
                return []
            stop = stop_record[0]
            lat = stop.latitude
            lon = stop.longitude
        records = (session.query(db_model.Stop.id).filter(
            text("earth_distance(ll_to_earth(:lat1, :lon1), ll_to_earth(latitude, longitude)) / 1000.0 <= :r1")
        ).filter(
            text('earth_distance(ll_to_earth(:lat1, :lon1), ll_to_earth(latitude, longitude)) / 1000.0 >= :r2')
        )
                .params(lat1=lat, lon1=lon, r1=radius_large, r2=radius_small))
        result = []
        for record in records:
            result.append(record.id)
        return result
    except Exception as e:
        print(f"query stops around stop(id :{stop_id} ) with error:", e)
    finally:
        session.close()


def update_all_json_str_to_json():
    session = Session()
    result = session.query(db_model.Stop).all()
    for record in result:
        json_obj = json.loads(record.line_id_to_sequence)
        record.line_id_to_sequence = json_obj
    session.commit()
    session.close()


def query_all_stops_linked(stop_id):
    session = Session()
    res = session.execute(text(
        f"""    select DISTINCT id
                FROM guangzhou_stop,
                (SELECT key as line_id, line_id_to_sequence ->> key as sequence FROM guangzhou_stop, json_each(line_id_to_sequence) 
                WHERE id = '{stop_id}' )s
                WHERE line_id_to_sequence -> line_id IS NOT NULL
                AND ABS((line_id_to_sequence ->> line_id)::numeric - sequence::numeric) = 1 
                ORDER BY id;"""
    ))
    session.close()
    return res.fetchall()


def query_all_stops_linked_x(stop_id, x):
    session = Session()
    res = session.execute(text(
        f"""    select DISTINCT id
                FROM guangzhou_stop,
                (SELECT key as line_id, line_id_to_sequence ->> key as sequence FROM guangzhou_stop, json_each(line_id_to_sequence) 
                WHERE id = '{stop_id}' )s
                WHERE line_id_to_sequence -> line_id IS NOT NULL
                AND ABS((line_id_to_sequence ->> line_id)::numeric - sequence::numeric) = {x} 
                ORDER BY id;"""
    ))
    session.close()
    return res.fetchall()


def query_all_stops_nearby(stop_id, x):
    session = Session()
    res = session.execute(text(
        f"""    select DISTINCT '{stop_id}' as start_id,id as end_id,line_id,seq,line_id_to_sequence ->> line_id as to_seq
                FROM guangzhou_stop,
                (SELECT key as line_id, line_id_to_sequence ->> key as seq FROM guangzhou_stop, json_each(line_id_to_sequence) 
                WHERE id = '{stop_id}' )s
                WHERE line_id_to_sequence -> line_id IS NOT NULL
                AND ABS((line_id_to_sequence ->> line_id)::numeric - seq::numeric) = {x} 
                ORDER BY id;"""
    ))
    session.close()
    return res.fetchall()


def query_all_lines_pass_through(stop_id):
    session = Session()
    res = session.execute(
        text(
            f"""SELECT json_object_keys(line_id_to_sequence) as line_id FROM guangzhou_stop WHERE id = '{stop_id}'"""
        )
    )
    session.close()
    return res.fetchall()


def query_vehicle_num():
    session = Session()
    res = session.query(func.count(db_model.Vehicle.id).label('num')).all()
    session.close()
    return res[0].num


def query_stop_num():
    session = Session()
    res = session.query(func.count(db_model.Stop.id).label('num')).all()
    session.close()
    return res[0].num


def all_stops():
    session = Session()
    res = session.execute(text("select * from guangzhou_stop"))
    session.close()
    return res.fetchall()


def insert_stop_nearby(start_id, des_id, line_id, st_seq, des_seq, line_cost, time, distance_e, distance_sp):
    session = Session()
    res = session.execute(text(f"""insert into stop_nearby 
            VALUES('{start_id}','{des_id}',{distance_e},
            {distance_sp},'{line_id}',{line_cost},{time},{st_seq},{des_seq});"""))
    session.commit()
    session.close()


def qe():
    session = Session()
    res = session.execute(text("select count(*) from stop_nearby"))
    session.close()
    return res.fetchall()


def query_stops_with_start_id_and_line_id(start_id, line_id):
    session = Session()
    res = session.execute(text(
        f"""select start_stop_id,end_stop_id,line_id from stop_nearby where start_stop_id = '{start_id}' and line_id = '{line_id}';"""))
    session.close()
    return res.fetchall()

def bucket_exist(bucket_id:int):
    session = Session()
    res = session.execute(text(
        f"""select count(*) from guangzhou_buckets where bucket_id = {bucket_id} ;"""
    ))
    session.close()
    num =  res.fetchall()
    return num[0][0] > 0

def stop_is_in_bucket(bucket_id:int,stop_id:str):
    session = Session()
    res = session.execute(text(
        f"""select count(*) from guangzhou_buckets where bucket_id = {bucket_id} and '{stop_id}' = ANY(stops);"""
    ))
    session.close()
    num = res.fetchall()
    print(num)
    return num[0][0] > 0

def insert_bucket(bucket_id:int):
    session = Session()
    res = session.execute(text(f"""insert into guangzhou_buckets (bucket_id) values ({bucket_id})"""))
    session.commit()
    session.close()
    
def update_bucket_s_stops_and_lines(bucket_id:int,stop_id:str,line_ids:list[str]):
    line_ids_str = ""
    for line_id in line_ids:
        line_ids_str += f""""{line_id}","""
    line_ids_str = line_ids_str[:-1]
    session = Session()
    session.execute(text(f"""update guangzhou_buckets set stops = array_append(stops,'{stop_id}'), lines = lines || '{{{line_ids_str}}}' where bucket_id = {bucket_id};"""))
    session.commit()
    session.close()

def update_or_insert_route_info(route_info:dict):
    start_stop_id = route_info["start"]
    end_stop_id = route_info["end"]
    cost = route_info["cost"] if "cost" in route_info else 0
    distance_euclid = route_info["distance_euclid"] if "distance_euclid" in route_info else 0
    distance_shortest_path = route_info["distance_sp"] if "distance_sp" in route_info else 0
    duration = route_info["duration"] if "duration" in route_info else 0
    polyline = route_info["polyline"] if "polyline" in route_info else ""
    via_stops = route_info["via_stops"] if "via_stops" in route_info else "[]"
    via_lines = route_info["via_lines"] if "via_lines" in route_info else "[]"
    conflict_dsp = route_info["distance_sp"] if "distance_sp" in route_info else "distance_shortest_path"
    conflict_cost = route_info["cost"] if "cost" in route_info else "cost"
    conflict_duration = route_info["duration"] if "duration" in route_info else "duration"
    conflict_polyline = route_info["polyline"] if "polyline" in route_info else "polyline"
    conflict_via_stops = route_info["via_stops"] if "via_stops" in route_info else "via_stops"
    conflict_via_lines = route_info["via_lines"] if "via_lines" in route_info else "via_lines"
    session = Session()
    res = session.execute(text(f"""
        insert into guangzhou_route_info (start_stop_id,end_stop_id,distance_euclid,distance_shortest_path,
                        cost,duration,polyline,via_stops,via_lines) values(
                            {start_stop_id},{end_stop_id},{distance_euclid},{distance_shortest_path},{cost},{duration},{polyline},{via_stops},{via_lines},
                        ) on conflict do
                        update set distance_shortest_path = {conflict_dsp}, cost = {conflict_cost}, duration = {conflict_duration}, polyline = {conflict_polyline}, via_stops = {conflict_via_stops}, via_lines = {conflict_via_lines};
                            """))
    session.commit()
    session.close()

def query_route_info(st_id:str,end_id:str):
    session = Session()
    res = session.execute(text(f"""select * from guangzhou_route_info where start_stop_id='{st_id}' and end_stop_id='{end_id}';"""))
    session.close()
    ret = res.fetchall()
    if len(ret) > 0:
        return True, ret
    else:
        return False, ret

def query_bucket_info(bucket_id):
    session = Session()
    res = session.execute(text(f"""select * from guangzhou_buckets where bucket_id="{bucket_id}";"""))
    session.close()
    return res.fetchall()

print(query_route_info(st_id='BV09110339',end_id='BV09110339'))
