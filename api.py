#!/usr/bin/python3

import json
import sys
import os

from bugge.bugge import Bugge
from bugge.bugge import DB_wrap

bugge = Bugge()
bugge.read_config("../../configs/testDB.txt")
bugge.init_DB()

@bugge.route("/forslag", "GET")
def show_forslag():
    cursor = bugge.get_DB_cursor()
    cursor.execute("select * from forslag")
    row_count = 0
    rows = []
    for row in cursor:
        row_count += 1
        rows += [row]

    response = [dict() for x in range(0, row_count)]
    row_count = 0
    for row in rows:
        response[row_count] = {
            "id": row[0],
            "title": row[1],
            "forslag": row[2]
        }
        row_count += 1

    bugge.respond_JSON(response)

# Reads the request from
# env.py if in debug,
# os.environ if not in debug (deploy)
bugge.handle_request()
