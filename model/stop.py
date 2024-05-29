import math

import util.transform as tf


class Stop(object):
    def __init__(self, pos: tuple[float, float], stop_id: str):
        self.stop_id = stop_id
        self.longitude = pos[0]
        self.latitude = pos[1]
        self.x, self.y = tf.wgs84_to_utm(pos)
        self.city_name = "guangzhou"

    def bucket_pos(self, origin, m, n):
        bucket_i = math.ceil(float(self.x - origin[0]) / n)
        bucket_j = math.ceil(float(self.y - origin[1]) / m)
        return bucket_i, bucket_j

    def pos(self):
        return self.longitude, self.latitude

    def utm_xy(self) -> tuple[float, float]:
        return self.x, self.y

    def point(self):
        return self.stop_id, self.longitude, self.latitude
