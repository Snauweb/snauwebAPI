#!/usr/bin/python3

import json
import sys
import os
import datetime
from urllib.parse import parse_qs

from bugge.bugge import Bugge
from bugge.bugge import DB_wrap

bugge = Bugge()
# Relative to launch directory

#bugge.read_config("../../configs/testDB.txt") # <- test db confi
bugge.read_config("../../configs/db.txt")  # deploy config
bugge.init_DB()


# As of now, any authenticated user is allowed to view the same user info
# Accepts id as a query parameter. If more ids, pick first
@bugge.route("/bruker", "GET")
def get_brukerinfo():
    cursor = bugge.get_DB_cursor()
    query_dict = parse_qs(bugge.env["QUERY_STRING"])

    # Dig up specified user data when requested by id
    if "id" in query_dict:
        query = \
            'SELECT username, firstname FROM \
            "tbl_User" AS u WHERE u.userid = %s'
        cursor.execute(query, [query_dict["id"][0]])

    # Otherwise, find the user id associated with the currently logged on user
    else:
        user = bugge.env["REMOTE_USER"]
        print("bruker", user, file=sys.stderr)
        # prune all the realm info from the name if needed
        # johan@AD.SAMFUNDET.NO -> johan
        if(not user.find('@') == -1):
            user = user[:user.find('@')]

        # Translate alias user name (from kerberos auth) into user_id,
        # use id to look up more user info
        query = \
            'SELECT username, firstname FROM \
            (SELECT brukerid FROM brukeralias where brukeralias.brukeralias = %s)\
            AS ids INNER JOIN "tbl_User" AS u ON ids.brukerid = u.userid;'
        
        cursor.execute(query, [user]);
            
    # Only one user should match, choose first found
    result = [];
    try:
        result = cursor.fetchone();
    except Exception:
        bugge.respond_error("JSON",
                            404,
                            error_msg="No user data found");
        return;

    response = [{
        "brukernavn": result[0],
        "fornavn": result[1]
    }]

    # Discard any items remaing in cursor, regardless of exceptions thrown
    try:
        cursor.close();
    except Exception:
        pass

    bugge.respond_JSON(response)



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
    # prune all the realm info from the name if needed
    # johan@AD.SAMFUNDET.NO -> johan
    if(not user.find('@') == -1):
        user = user[:user.find('@')]
        
    # What is the ID of the current user?
    id_query = \
        'SELECT brukerid FROM brukeralias WHERE brukeralias.brukeralias = %s';

    id_query_cursor = bugge.get_DB_cursor()
    id_query_cursor.execute(id_query, [user])
    # Only one user should match, choose first found
    user_id = id_query_cursor.fetchone();

    # Discard any items remaing in cursor, regardless of exceptions thrown
    try:
        id_query_cursor.close();
    except Exception:
        pass

    # If no id is found, the alias table is misconfigured
    if(user_id == None):
        bugge.respond_error("JSON",
                            500,
                            error_msg="Server could not find user id")
        return
        
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
        "INSERT INTO forslag (tittel, forslag, lagt_til, brukerid)\
        VALUES (%s, %s, %s, %s)"
    cursor = bugge.get_DB_cursor()
    cursor.execute(query, [tittel, forslag, date_string, user_id])
    bugge.DB.connection.commit()
    bugge.respond_JSON(payload_dict, status=201)
    cursor.close()

@bugge.route("/forslag", "GET")
def show_forslag():
    cursor = bugge.get_DB_cursor()
    cursor.execute("SELECT * FROM forslag ORDER BY lagt_til DESC")
    row_count = 0
    rows = []
    for row in cursor:
        row_count += 1
        rows += [row]

    response = [{} for x in range(0, row_count)]
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
