#!/usr/bin/python3

import json
import sys
import os
import datetime

from bugge.bugge import Bugge
from bugge.bugge import DB_wrap

bugge = Bugge()
bugge.read_config("../../configs/config_pg_test.txt")
bugge.init_DB()

@bugge.route("/forslag", "POST")
def add_forslag():
    bugge.read_payload()
    payload_dict = bugge.parse_payload_json()
    if (payload_dict == None):
        bugge.respond_error("JSON",
                            422,
                            error_msg="The provided json payload was malformed")
        return


    user = bugge.env["REMOTE_USER"]
    date = datetime.datetime.now()
    date_string = str(date)
    date_string = date_string[:date_string.find(".")]
    tittel = payload_dict["tittel"]
    forslag = payload_dict["forslag"]

    if(tittel == "" or forslag == ""):
        bugge.respond_error("JSON",
                            422,
                            error_msg=\
                            "The provided json payload lacked tittel and or forslag")
        return
    
    query = \
        "INSERT INTO forslag (tittel, forslag, lagt_til, brukernavn)\
        VALUES (%s, %s, %s, %s)"
    cursor = bugge.get_DB_cursor()
    cursor.execute(query, [tittel, forslag, date_string, user])
    bugge.DB.connection.commit()
    
    bugge.respond_JSON(payload_dict, status=201)
    cursor.close()

@bugge.route("/forslag", "GET")
def show_forslag():
    cursor = bugge.get_DB_cursor()
    cursor.execute("SELECT * FROM forslag")
    row_count = 0
    rows = []
    for row in cursor:
        row_count += 1
        rows += [row]

    response = [dict() for x in range(0, row_count)]
    row_count = 0
    for row in rows:
        response[row_count] = {
            "tittel": row[1],
            "forslag": row[2],
            "lagt_til": str(row[3])
        }
        row_count += 1
        
    bugge.respond_JSON(response)

# Reads the request from
# env.py if in debug,
# os.environ if not in debug (deploy)
bugge.handle_request()
