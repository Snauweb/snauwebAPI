#!/usr/bin/python3

import json
import sys
import os
import datetime
from urllib.parse import parse_qs

from bugge.bugge import Bugge
from bugge.bugge import DB_wrap

import api_utils

# API framework class
bugge = Bugge()


# If configLocation file exists, use it. Otherwise use hard coded default
configPath = "../configs/config.txt" # <- Default
try:
    from configLocation import configLocation
    configPath = configLocation

# if no file exists python will get mad. Catch the excption here with a noop
# This makes the framework fall back to the defult defined above
except: 
    pass

bugge.read_config(configPath)
bugge.init_DB()


# Add or remove a reaction.
# Normally, you can only add or remove reactions on your own behalf
# Payload is {[brukerid: <id>], forslagid: <id>, reaksjonstypeid: <id>}
# brukerid is optional, and only relevant for superusers. Normal users
# trying to react on someone elses behalf must be stopped and sent a 403 forbidden message.
# When brukerid is not specified, the id of the currently logged in user is used
# Query parameters are not used


# TODO The validation logic in this endpoint is probably usefull elsewhere
# Make a proper helper function for it. If too expensive, offload to the DB engine
# to reject/accept. Probably more efficient, but less information about the error can
# be returned to API user
@bugge.route("/reaksjon", "POST")
def react_to_forslag():
    cur_user_id = api_utils.get_cur_user_id(bugge, DB_wrap)

    # Read and validate payload
    bugge.read_payload()
    payload_dict = bugge.parse_payload_json()
    if (payload_dict == None):
        bugge.respond_error("JSON",
                            422,
                            error_msg="The provided JSON payload was not valid JSON")
        return

    # Then we check the payload contents.
    # First we extract and validate all fields.
    # Unexpected fields are disregarded. Expected fields with illegal values return a 422
    # All fields have default values
    expected_fields = {"forslagid": None, "reaksjonstypeid": None}
    optional_fields = {"brukerid": cur_user_id}
    invalid_fields = []
    invalid_request = False

    # If a required fileld is absent, respond with 422
    for key in expected_fields:
        try:
            value = payload_dict[key]
        except:
            bugge.respond_error("JSON", 422, error_msg="lacking expected field " + key)
            return
        
        if(api_utils.is_valid_id(value) == False):
            invalid_request = True
            invalid_fields.append((key, value, "not a valid id number"))

        # Valid field, update expected_fields
        else:
            expected_fields[key] = value;
    

    # If an optional field is absent, we just move on
    # All optional fields have automatic defaults
    for key in optional_fields:
        try:
            value = payload_dict[key]
        except:
            continue

        value = payload_dict[key]
        if(api_utils.is_valid_id(value) == False):
            invalid_request = True
            invalid_fields.append((key, value, "not a valid id number"))

            # The supplied brukerid might be a valid id,
            # but is the user authorised to use it?
            # By default, the brukerid in the payload must match 
        elif(key == "brukerid" and not(value == cur_user_id)):
            invalid_request = True
            invalid_fields.append(
                (key, value, "requesting user not authorised to react on behalf of others")
            )

        # Valid field, update expected_fields
        else:
            optional_fields[key] = value;



    # Invalid requests returns a 422 with an explanation
    if(invalid_request == True):
        error_msg = ""
        for (key, value, description) in invalid_fields:
            error_msg += ("error in pair " + key + " - " + value + ": " + description + "; ")

        error_msg = error_msg[:len(error_msg)-1] # Prune final newline
        bugge.respond_error("JSON", 422, error_msg=error_msg)
        return

    # If we get here, we are looking at a legal request
    # But is it valid wrt database state? Namely:
    #     1. Does the requested reaksjonsid exist?
    #     2. Does the requested forslag exist?
    #     3. (in case of superuser) does the requested brukerid exist?
    # This is handeled by internal DB constraints

    # It's an unreact if the react allready exists

    # Does not select any columns, as they are not needed
    select_query = """
    SELECT FROM forslag_reaksjon 
    WHERE brukerid=%s AND forslagid=%s AND reaksjonstypeid=%s
    """

    insert_query = """
    INSERT INTO forslag_reaksjon VALUES (%s, %s, %s)
    """

    delete_query = """
    DELETE FROM forslag_reaksjon 
    WHERE brukerid=%s AND forslagid=%s AND reaksjonstypeid=%s    
    """

    select_cursor = bugge.get_DB_cursor()
    edit_cursor = bugge.get_DB_cursor()

    select_cursor.execute(select_query,
                          [
                              optional_fields["brukerid"],
                              expected_fields["forslagid"],
                              expected_fields["reaksjonstypeid"]
                          ])

    existing_react = select_cursor.fetchone()

    # Insert if the react does not exist, delete if it does
    if(existing_react == None):
        edit_cursor.execute(insert_query,
                            [
                                optional_fields["brukerid"],
                                expected_fields["forslagid"],
                                expected_fields["reaksjonstypeid"]
                            ])
    else:
        edit_cursor.execute(delete_query,
                            [
                                optional_fields["brukerid"],
                                expected_fields["forslagid"],
                                expected_fields["reaksjonstypeid"]
                            ])

    
    # Commit the queries using the DB connection contained in Bugge
    # For some reason this is required when altering the database, but not when reading
    bugge.DB.connection.commit()

    # Try catch to ensure no exceptions even if the cursors contain stuff for some reason
    try:
        select_cursor.close()
    except:
        pass

    try:
        edit_cursor.close()
    except:
        pass

    # Return the new count, this is more efficient than performing a round-trip over the net
    result = api_utils.get_single_reaction_count(expected_fields["forslagid"],
                                                 cur_user_id, bugge, DB_wrap)
    # Return a count of 0 if no reactions are found
    if(result == None):
        response = {
            "forslagid": expected_fields["forslagid"],
            "numReaksjoner" : 0,
            "curUserReacted" : False
        }
        
        # Otherwise, return the found count
    else:
        response = {
            "forslagid": expected_fields["forslagid"],
            "numReaksjoner" : result[0],
            "curUserReacted" : result[1]
        }

    bugge.respond_JSON(response)

    
        

# Get reaction info for forslag. If forslagid is specified, a specific forslag is returned
# If id is specified, the count and type for all forslag present in the database is returned
@bugge.route("/reaksjon", "GET")
def get_reactions():
    cur_user_id = api_utils.get_cur_user_id(bugge, DB_wrap)
    
    query_dict = parse_qs(bugge.env["QUERY_STRING"])
    reaction_query = ""
    response = "no data"
    # Return number of reactions for given id
    if("id" in query_dict):
        forslagid = query_dict["id"][0]

        result = api_utils.get_single_reaction_count(forslagid, cur_user_id, bugge, DB_wrap)
        # Return a count of 0 if no reactions are found
        if(result == None):
            response = {
                "forslagid": forslagid,
                "numReaksjoner" : 0,
                "curUserReacted" : False
            }

        # Otherwise, return the found count
        else:
            response = {
                "forslagid": forslagid,
                "numReaksjoner" : result[0],
                "curUserReacted" : result[1]
            }


    # If no id is given, list all
    else:
        rows = api_utils.get_all_reaction_counts(cur_user_id, bugge, DB_wrap)

        response = [{} for x in range(0, len(rows))]
        row_count = 0
        for row in rows:
            response[row_count] = {
                "forslagid": row[0],
                "numReaksjoner" : row[1],
                "curUserReacted" : row[2]
            }

            row_count += 1
         

        
    # Return the completed response
    bugge.respond_JSON(response)

    
    


# Shows all active aliases
@bugge.route("/bruker/alias", "GET")
def get_active_aliases():
    cursor = bugge.get_DB_cursor()

    query = \
        'SELECT username, brukeralias FROM \
        (SELECT userid, username from "tbl_User") AS u \
        INNER JOIN brukeralias AS b ON u.userid = b.brukerid \
        '

    cursor.execute(query);
    
    row_count = 0
    rows = []
    for row in cursor:
        row_count += 1
        rows += [row]

    response = [{} for x in range(0, row_count)]
    row_count = 0
    for row in rows:
        response[row_count] = {
            "brukernavn": row[0],
            "brukeralias": row[1],
        }
        row_count += 1
        
    bugge.respond_JSON(response) 
    
    cursor.close()

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

    # Another null check
    if(result == None):
        bugge.respond_error("JSON",
                            404,
                            error_msg="No user data found");
        return

    # At this point, we know we found something. Pack it up and return it
    response = {
        "brukernavn": result[0],
        "fornavn": result[1],
        "etternavn" : result[2]
    }

    # Discard any items remaing in cursor. If any items do remain,
    # this will cause an exception. We ignore it.
    try:
        cursor.close();
    except Exception:
        pass

    bugge.respond_JSON(response)



# This endpoint auto-includes the currently logged in user, and marks the forslag as ny (status 1)
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
        "INSERT INTO forslag (tittel, forslag, lagt_til, brukerid, statusid)\
        VALUES (%s, %s, %s, %s, %s)"
    cursor = bugge.get_DB_cursor()
    cursor.execute(query, [tittel, forslag, date_string, user_id, 1])
    bugge.DB.connection.commit()
    bugge.respond_JSON(payload_dict, status=201)
    cursor.close()

# Must support filtering what forslag is selected. Use query parameters for this
# Recognised parameters:
# sorter = <[dato|stemmer|kategori]>-<[asc|desc]>
# kategorier = [<list>]
# sok = <substreng>
#
# sok supports regular expressions to some extent, not sure what special characters
# are removed when the prepared statement algorithm is run. It matches both
# header and body of forslag.
# A match in either means the forslag is included in the response
@bugge.route("/forslag", "GET")
def show_forslag():
    # First all parameters must be prepared
    # What user is currently logged on?
    cur_user_id = api_utils.get_cur_user_id(bugge, DB_wrap)

    # Then we must construct the parts of the query that depends on the query
    query_dict = parse_qs(bugge.env["QUERY_STRING"])

    # First the ordering. If no ordering parameter is specified,
    # sort by date descending.
    forslag_query_sort = "ORDER BY lagt_til DESC"
    if("sorter" in query_dict):
        sorter_value = query_dict["sorter"][0] #Should only be one value for this parameter
        (field, order) = sorter_value.split('-')
        (field, order) = (field.lower(), order.upper())

        param_is_valid = False
        
        # Parameter must be of a valid value
        # This is important to make sure user input does not contain SQL and such
        if(field in ["dato", "stemmer", "kategori"] and order in ["ASC", "DESC"]):
            param_is_valid = True

        # No user input is included directly
        if(param_is_valid):
            if(field == "dato"):
                field = "lagt_til"

            if(field == "stemmer"):
                field = "num_reaksjoner"

            if(field == "kategori"):
                field = "forslag.statusid"
            
            forslag_query_sort = "ORDER BY " + field + " " + order

        # Illegal parameters should return a 422
        else:
            bugge.respond_error("JSON",
                                422,
                                error_msg=\
                                "Illegal value for query parameter sorter: " + sorterValue)
            return


    # To filter on categories, we use the IN <tuple> sql expression
    valid_category_ids = api_utils.get_valid_category_ids(bugge, DB_wrap)
    included_categories = valid_category_ids # Default is to include all valid categories
    
    # If the query parameters specifies categories,
    # check what valid ids are indcluded and add them
    if("kategorier" in query_dict):
        
        # Loop through all requested kategorier, look for valid ones
        requested_category_list = query_dict["kategorier"][0].split(',')
        included_categories = [] # Start with an empty list
        for category in requested_category_list:
            # We must parse the category as int to compare it to the id list
            category_as_int = -1
            try:
                category_as_int = int(category)
            except Exception:
                continue #a non-int "category id" is ignored, try the next one
                
                
            if(category_as_int in valid_category_ids):
                included_categories.append(category_as_int)
                    
        
    # Now we need to check if any valid category ids made it. If not,
    # the query fragment must be set to "true" to not give a syntax error
    # (The postgres SQL dialect does not permit an empty tuple in an IN expression)

    forslag_query_category = "true"

    # If a list of kategoriids were provided but none were valid, return nothing
    if(len(included_categories) == 0):
        forslag_query_category = "false"
    
    # A single-item tuple is printed with an extra comma we don't want.
    # Needs separate handling
    if(len(included_categories) == 1):
        forslag_query_category = \
            " (forslag.statusid in(" + str(included_categories[0]) + ")) "

    # The built in stringification of tuples otherwise does what we want
    if(len(included_categories) > 1):
        forslag_query_category = \
            " (forslag.statusid in" + str(tuple(included_categories)) + ") "
        
    # Then we must add the search parameter. By default nothing
    # As this is free text, it must be added as a parameter to the prepared statement
    sok_value = ".*" # by default, match all
    forslag_query_sok = " (tittel ~ %s OR forslag ~ %s) "
    if("sok" in query_dict):
        sok_param_value = query_dict["sok"][0]
         # As this is included in a prepared statement,
         # copying query string verbatim should be safe
        sok_value = sok_param_value
    
    cursor = bugge.get_DB_cursor()
    forslag_query_base =\
        """
        SELECT forslag.forslagid, tittel, forslag, lagt_til, brukerid, forslag.statusid,
        forslagstatus.beskrivelse,
        CASE WHEN reaksjoner.num_reaksjoner is 
        NULL THEN 0 ELSE reaksjoner.num_reaksjoner END as num_reaksjoner,
        CASE WHEN reaksjoner.cur_user_reacted is 
        NULL THEN FALSE ELSE reaksjoner.cur_user_reacted END as cur_user_reacted
        
        FROM forslag INNER JOIN forslagstatus ON
        forslag.statusid = forslagstatus.statusid
        LEFT JOIN (
        SELECT forslagid, 
                   count(*) AS num_reaksjoner, 
                   bool_or(brukerid=%s) AS cur_user_reacted
            FROM forslag_reaksjon 
            GROUP BY forslagid
        ) AS reaksjoner
        ON reaksjoner.forslagid = forslag.forslagid
        """

    forslag_query = (
        forslag_query_base +
        " WHERE " +
        forslag_query_category +
        " AND " +
        forslag_query_sok +
        forslag_query_sort
    )
    
    print(forslag_query, file = sys.stderr)
    
    SQL_query_params = [cur_user_id, sok_value, sok_value]
    
    cursor.execute(forslag_query, SQL_query_params)
    
    row_count = 0
    rows = []
    for row in cursor:
        row_count += 1
        rows += [row]
        
    response = [{} for x in range(0, row_count)]
    row_count = 0
    for row in rows:
        response[row_count] = {
            "forslagid": row[0],
            "tittel": row[1],
            "forslag": row[2],
            "lagt_til": str(row[3]),
            "statusid": row[5],
            "statusbeskrivelse": row[6],
            "num_reaksjoner": row[7],
            "cur_user_reacted": row[8]
        }
        row_count += 1

    cursor.close()
    bugge.respond_JSON(response)

# The api root should contain instructions for api use
@bugge.route("/", "GET")
def show_help():
    bugge.respond_HTML("<h1>Snauweb API</h1> <p>Her burde det stå instruksjoner for API-bruk")

# Reads the request from
# env.py if in debug,
# os.environ if not in debug (deploy)
bugge.handle_request()
