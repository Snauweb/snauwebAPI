
def setup_routes(bugge):
    setup_POST(bugge)
    setup_GET(bugge)


def setup_GET(bugge):
    # Get reaction info for forslag. If forslagid is specified,
    # a specific forslag is returned
    # If id is specified, the count and type for all forslag
    # present in the database is returned
    @bugge.route("/reaksjon", "GET")
    def get_reactions():
        cur_user_id = api_utils.get_cur_user_id(bugge)

        if(cur_user_id == -1):
            bugge.respond_error("JSON", 403,
                                error_msg="The current user was not found in alias list")
            return


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
def setup_POST(bugge):
    @bugge.route("/reaksjon", "POST")
    def react_to_forslag():
        cur_user_id = api_utils.get_cur_user_id(bugge)

        if(cur_user_id == -1):
            bugge.respond_error("JSON", 403,
                                error_msg="The current user was not found in alias list")
            return

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
                    (key,
                     value,
                     "requesting user not authorised to react on behalf of others")
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
        bugge.commit_DB()

        # Try catch to ensure no exceptions
        # even if the cursors contain stuff for some reason
        try:
            select_cursor.close()
        except:
            pass

        try:
            edit_cursor.close()
        except:
            pass

        # Return the new count, this is more efficient than
        # performing a round-trip over the net
        result = api_utils.get_single_reaction_count(
            expected_fields["forslagid"],
            cur_user_id, bugge, DB_wrap
        )
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
