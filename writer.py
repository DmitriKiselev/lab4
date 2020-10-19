#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
Template doc
"""
import argparse
import time
import json
import sqlite3

import numpy as np

from cryptography.fernet import Fernet


def rescale(value, old_min, old_max, new_min, new_max):
    rescaled = (((value - old_min) * (new_max - new_min)) /
                (old_max - old_min)) + new_min
    return rescaled


class Writer:

    def __init__(self, db_path, key_path, period):
        self.db_path = db_path
        self.key_path = key_path
        self.period = period

    def write(self):
        # creating or connecting to db
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        if ('data',) not in cursor.fetchall():
            cursor.execute("""CREATE TABLE data(pressure_value, 
                              temprature1_value, temprature2_value, co2_value, 
                              humidity_value, distance_value, fuel_value)
                        """)
        sql = ''' INSERT INTO data(pressure_value, temprature1_value, 
                                temprature2_value, co2_value, humidity_value, 
                                distance_value, fuel_value)
                  VALUES(?,?,?,?,?,?,?) '''

        start = time.time()
        # generate key
        key = Fernet.generate_key().decode(encoding="utf-8")
        dict = {'key': key}
        # saving key
        with open(self.key_path, 'w') as outfile:
            json.dump(dict, outfile)
        f = Fernet(key)
        while 1:
            if time.time() - start == self.period:
                # generation and encryption of data
                pressure_sensor = f.encrypt(str(np.random.lognormal(0.5, 0.4))
                                            .encode("utf-8"))
                t1_sensor = f.encrypt(str(rescale(np.random.power(0.5), 0, 1,
                                                  -40, 120)).encode("utf-8"))
                t2_sensor = f.encrypt(str(np.random.normal(20, 15)).
                                      encode("utf-8"))
                co2_sensor = f.encrypt(str(np.random.uniform(400, 2000)).encode
                                       ("utf-8"))
                humidity_sensor = np.random.laplace(loc=0.0, scale=1.0,
                                                    size=None)
                humidity_sensor = f.encrypt(str(rescale(
                    humidity_sensor, -5, 5, 10, 99)).encode("utf-8"))
                distance_sensor = np.random.power(0.7)
                distance_sensor = f.encrypt(str(rescale(
                    distance_sensor, 0, 1, 0.1, 10)).encode("utf-8"))
                fuel_sensor = f.encrypt(str(np.random.uniform(0, 45)).encode
                                        ("utf-8"))
                # saving ecrypted data
                data = (pressure_sensor, t1_sensor, t2_sensor,
                        co2_sensor,
                        humidity_sensor, distance_sensor, fuel_sensor)
                print('Data generated')
                cursor.execute(sql, data)
                conn.commit()
                start = time.time()


def get_args():
    """Arguments parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db_path', default='data.db',
                        help='Path for db file')
    parser.add_argument('--key_path', default='key.json',
                        help='Path for json with generated key')
    parser.add_argument('--period', default=5,
                        help='Period of generation new data (in seconds)')
    return parser.parse_args()


def main():
    """Application entry point."""
    args = get_args()
    writer_1 = Writer(args.db_path, args.key_path, args.period)
    writer_1.write()

if __name__ == '__main__':
    main()
