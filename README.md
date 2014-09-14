mongocsvimporter
================

Typed (annotated) CSV importer for Mongo (based on mongoimporter). Each column in the CSV file is given a type and it is converted as each line is read.

Types:

    * `s` string
    * `i` integer
    * `f` float
    * `d` datetime

Usage
=====

Use Python 3.4:

    $ python mongoimporttypedcsv.py --help

The following will `drop` the existing mongodb table, import the name CSV `filename`, use the Windows `cp1252` encoding, into the specified mongo `db` and `collection`. `type` specifies the types for 16 fields and `fields` gives a title to each for their mongo keys.

    $ python mongoimporttypedcsv.py --drop --filename=/home/ian/data/land_registry/pp-2014.csv --encoding=cp1252 --db=land_registry --collection=sales --types s i d s s s s s s s s s s s s --fields id price date postcode type old_new dur paon saon street locality town local_auth country status

The example above is based on UK Land Registry open data http://data.gov.uk/dataset/land-registry-monthly-price-paid-data

NOTE the first line of the CSV cannot (yet) be ignored, so it can't have a header.

Testing
=======

To run the unit-tests

    $ nosetests mongoimporttypedcsv.py

