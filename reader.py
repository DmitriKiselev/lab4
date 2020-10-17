#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
Template doc
"""
import argparse
import json
import sqlite3

from cryptography.fernet import Fernet
from tensorboardX import SummaryWriter


def get_args():
    """Arguments parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db_path', default='data.db',
                        help='Path for db file')
    parser.add_argument('--key_path', default='key.json',
                        help='Path for json with generated key')

    return parser.parse_args()


def read(db_path, key_path):
    with open(key_path, 'r') as read_file:
        key = json.load(read_file)
    key = key['key'].encode('utf-8')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM data""")
    a = cursor.fetchall()
    new_len = len(a)
    old_len = new_len
    writer = SummaryWriter('/home/dmitry/runs/lab2')
    iter = 0
    while 1:
        cursor.execute("""SELECT * FROM data""")
        a = cursor.fetchall()
        f = Fernet(key)
        if iter == 0:
            for i in range(len(a)):
                writer.add_scalar('pressure_sensor', float((f.decrypt
                                  (a[i][0])).decode('utf-8')), i)
                writer.add_scalar('t1_sensor', float(((f.decrypt
                                  (a[i][1]))).decode('utf-8')), i)
                writer.add_scalar('t2_sensor', float((f.decrypt
                                  (a[i][2])).decode('utf-8')), i)
                writer.add_scalar('co2_sensor', float((f.decrypt
                                  (a[i][3])).decode('utf-8')), i)
                writer.add_scalar('humidity_sensor', float((f.decrypt
                                  (a[i][4])).decode('utf-8')), i)
                writer.add_scalar('distance_sensor', float((f.decrypt
                                  (a[i][5])).decode('utf-8')), i)
                writer.add_scalar('fuel_sensor', float((f.decrypt
                                  (a[i][6])).decode('utf-8')), i)
                writer.flush()
            iter=+1

        if new_len > old_len:
                writer.add_scalar('pressure_sensor',float((f.decrypt
                                  (a[-1][0])).decode('utf-8')), iter)
                writer.add_scalar('t1_sensor', float((f.decrypt
                                  (a[-1][1])).decode('utf-8')), iter)
                writer.add_scalar('t2_sensor', float((f.decrypt
                                  (a[-1][2])).decode('utf-8')), iter)
                writer.add_scalar('co2_sensor', float((f.decrypt
                                  (a[1][3])).decode('utf-8')), iter)
                writer.add_scalar('humidity_sensor', float((f.decrypt
                                  (a[-1][4])).decode('utf-8')), iter)
                writer.add_scalar('distance_sensor', float((f.decrypt
                                  (a[-1][5])).decode('utf-8')), iter)
                writer.add_scalar('fuel_sensor', float((f.decrypt
                                  (a[-1][6])).decode('utf-8')), iter)
                writer.flush()
                iter+=1
                old_len = new_len

        new_len = len(a)


def main():
    """Application entry point."""
    args = get_args()
    read(args.db_path, args.key_path)


if __name__ == '__main__':
    main()
