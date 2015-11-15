#! /usr/bin/env python

import ujson
import fileinput
import arango
from arango import Arango
from pprint import pprint

dbcnx = Arango(host="localhost")
try:
    dbcnx.delete_database("eris0")
except arango.exceptions.DatabaseDeleteError:
    pass
dbcnx.create_database("eris0")
db = dbcnx.database("eris0")
db.create_collection("events")
col = db.collection("events")
col.wait_for_sync = False


def main():
    for line in fileinput.input():
        line = line.strip()
        event = None
        try:
            event = ujson.loads(line)
        except ValueError:
            continue
        event["_key"] = event["id"]
        del event["id"]
        col.create_document(event)


main()
