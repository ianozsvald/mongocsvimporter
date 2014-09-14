#!/usr/bin/env python
"""Import a CSV file to Mongo with types for each column"""
import argparse
import time
import csv  # assumes Unicode csv in Python 3.4
import datetime
import pprint
from collections import OrderedDict
import unittest
import pymongo
from dateutil import parser as dt_parser

# Use Python 3.4
# %run mongoimporttypedcsv.py --help

# To run the unit-tests
# $ nosetests mongoimporttypedcsv.py

# The goal is to make a better mongoimport, based on
# http://docs.mongodb.org/manual/reference/program/mongoimport/
# by supporting types on each column, this will address:
# https://jira.mongodb.org/browse/SERVER-3731
# https://jira.mongodb.org/browse/SERVER-9015
# https://groups.google.com/forum/#!topic/mongodb-user/bYmlA4y-JDk
# e.g. "000123" gets turned into int 123
# http://grokbase.com/t/gg/mongodb-user/11bffzgwj4/mongoimport-csv-and-boolean-values

# For better type control maybe I should consider
# https://github.com/santiagobasulto/smartcsv/blob/master/README.md

# NOTE dataset cost 80sec bulk insert (5000 items at a time) vs 120s one at a
# time

mappers = {'s': str,
           'i': int,
           'f': float,
           'd': dt_parser.parse}


class Test(unittest.TestCase):
    def test1(self):
        """Check string, integer, float parsing"""
        line = dict({'name': 'ian', 'age': '22', 'price': '-99.3'})
        fieldnames_to_types = OrderedDict([('name', 's'), ('age', 'i'), ('price', 'f')])
        converted_line = convert_line(line, fieldnames_to_types)
        self.assertEqual(converted_line, ['ian', 22, -99.3])

    def test2(self):
        """Check date parsing"""
        line = dict({'name': 'ian', 'dt': "2014-04-17 00:00"})
        fieldnames_to_types = OrderedDict([('name', 's'), ('dt', 'd')])
        converted_line = convert_line(line, fieldnames_to_types)
        self.assertEqual(converted_line, ['ian', datetime.datetime(2014, 4, 17)])


def convert_line(line, fieldnames_to_types):
    """Convert a line and types into parsed line"""
    result = []
    for k, v in fieldnames_to_types.items():
        item = line[k]
        converted = mappers[v](item)
        result.append(converted)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Project description')
    parser.add_argument('--filename', help='CSV file to read')
    parser.add_argument('--encoding', default='UTF-8', help='Defaults to UTF8, might also be CP1252')
    parser.add_argument('--db', help='Destination MongoDB db')
    parser.add_argument('--collection', help='Destination MongoDB collection')
    parser.add_argument('--drop', default=False, action="store_true", help="Drop existing database (default: don't drop")
    parser.add_argument('--fields', type=str, nargs="*", help="Space separated list of field names e.g. --fields name age dob")
    parser.add_argument('--types', type=str, nargs="*", help="Space separated list of field types (s=string, d=datetime, i=integer) e.g. --types s i d")
    args = parser.parse_args()
    print(args)

    fieldnames = args.fields
    types = args.types

    conn = pymongo.Connection()
    db = conn[args.db]
    coll = db[args.collection]

    if args.drop:
        coll.drop()

    print("Args and types:")
    pprint.pprint([x for x in zip(fieldnames, types)])

    # use OrderedDict to preserve the order of the fields
    fieldnames_to_types = OrderedDict(zip(fieldnames, types))
    assert len(types) == len(fieldnames), "Fieldnames and Types must agree in length"

    line_nbr = 0
    t1 = time.time()
    with open(args.filename, "r", encoding=args.encoding) as f:
        reader = csv.DictReader(f, fieldnames)
        for line in reader:
            #print("Reading line nbr", line_nbr)
            converted_line = convert_line(line, fieldnames_to_types)
            fieldnames_and_fields = dict(zip(fieldnames, converted_line))
            coll.insert(fieldnames_and_fields)
            line_nbr += 1
    print("Reading took {}s".format(time.time() - t1))
