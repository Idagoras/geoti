from sqlalchemy import Column, Integer, String, ARRAY, DateTime, Float, Text, REAL, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum
import json

Base = declarative_base()


class VehicleType(PyEnum):
    NORMAL_BUS = 0
    SUBWAY_LIGHT_RAIL = 1
    AIRPORT_BUS_TO = 2
    TRAM = 3
    AIRPORT_BUS_FROM = 4
    TOURIST_BUS = 5
    NIGHT_BUS = 6
    AIRPORT_BUS_BETWEEN = 7
    FERRY = 8
    OTHER = 9
    EXPRESS_BUS = 10
    SLOW_BUS = 11
    AIRPORT_FAST_RAIL_TO = 12
    AIRPORT_FAST_RAIL_FROM = 13
    AIRPORT_RAIL_LOOP = 14


class Vehicle(Base):
    __tablename__ = 'guangzhou_vehicle'
    id = Column(String(length=50), primary_key=True)
    line_name = Column(String(length=50))
    vehicle_type = Column(Enum(VehicleType), default=VehicleType.NORMAL_BUS)
    stop_num = Column(Integer)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, default=datetime.utcnow)
    polyline = Column(Text)
    basic_price = Column(REAL)
    total_price = Column(REAL)
    direc = Column(String(length=50))

    def __init__(self, line_id, line_name, vehicle_type, stop_num, start_time, end_time, polyline, basic_price,
                 total_price,
                 direc):
        self.id = line_id
        self.line_name = line_name
        self.vehicle_type = vehicle_type
        self.stop_num = int(stop_num)
        self.start_time = start_time
        self.end_time = end_time
        self.polyline = polyline
        self.basic_price = basic_price
        self.total_price = total_price
        self.direc = direc


class Stop(Base):
    __tablename__ = 'guangzhou_stop'
    id = Column(String, primary_key=True)
    stop_name = Column(String(length=50))
    longitude = Column(REAL)
    latitude = Column(REAL)
    line_id_to_sequence = Column(JSON)

    def __init__(self, stop_id, line_id, stop_name, longitude, latitude, sequence):
        self.id = stop_id
        self.stop_name = stop_name
        self.longitude = longitude
        self.latitude = latitude
        l2s = {line_id:sequence}
        self.line_id_to_sequence = json.dumps(l2s)
