def setup_routes(bugge):
    setup_POST(bugge)
    setup_PUT(bugge)
    setup_DELETE(bugge)
    setup_GET(bugge)



def setup_POST(bugge):
    # This endpoint auto-includes the currently logged in user,
    # and marks the forslag as ny (status 1)
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
        bugge.commit_DB()
        bugge.respond_JSON(payload_dict, status=201)
        cursor.close()
    
def setup_PUT(bugge):
    # Update an existing forslag.
    # Payload specifies what is getting updated
    # Initially only set up to look for forslag status updates
    # Using PUT over PATCH as it is more common (?)
    @bugge.route("/forslag", "PUT")
    def update_forslag():

        bugge.read_payload()
        payload_dict = bugge.parse_payload_json()

        if(payload_dict == None):
            bugge.respond_error(
                response_type="JSON",
                error_code=422,
                error_msg="malformed payload"
            )
            return

        # Only valid edits are of status, thus statusid is a required field
        required_fields = ["forslagid", "statusid"]
        for field in required_fields:
            if field not in payload_dict:
                bugge.respond_error(
                    response_type="JSON",
                    error_code=422,
                    error_msg=("payload lacking required field " + field)
                )
                return


        # unlike for posting and deleting, editing a forslag requires
        # special permission. Check it
        cur_user_id = api_utils.get_cur_user_id(bugge, DB_wrap)

        if(cur_user_id == -1):
            bugge.respond_error("JSON", 403,
                                error_msg="The current user was not found in alias list")
            return


        cur_user_forslag_permissions = api_utils.get_permissions(
            cur_user_id, 'forslag', bugge)


        forslag_id = payload_dict["forslagid"]
        new_status_id = payload_dict["statusid"]

        # Now we must check the owner of the forslag
        owner_cursor = bugge.get_DB_cursor()
        owner_query = \
            """
            SELECT brukerid FROM forslag WHERE forslagid=%s
            """

        owner_cursor.execute(owner_query, [forslag_id])
        owner_result = owner_cursor.fetchone()

        # We only expect one result. Try catch just in case
        try:
            owner_cursor.close();
        except Exception:
            pass 

        # If the requested forslag is not in database return a 404
        if(owner_result == None):
            bugge.respond_error(
                response_type="JSON",
                error_code=404,
                error_msg= \
                "Failed to update forslag with id " + forslag_id + \
                " no such forslag in database"
            )
            return

        owner_result_id = owner_result[0] # unpack result id from tuple

        # Is this user allowed to update?
        if("redigere" not in cur_user_forslag_permissions):
            bugge.respond_error("JSON", 403,
                                error_msg=\
                                ("Unauthorised to update forslag with id " +
                                 forslag_id))
            return


        # At this point, everything should be in order, we can start the update
        update_query = \
            """
            UPDATE forslag
            SET statusid=%s
            WHERE forslagid=%s
            """
        update_cursor = bugge.get_DB_cursor()
        update_cursor.execute(update_query, [new_status_id, forslag_id])
        bugge.commit_DB()
        update_cursor.close()

        # All is well, respond with a 200
        bugge.respond_JSON({
            "forslagid": forslag_id,
            "statusid": new_status_id
        })

def setup_DELETE(bugge):
    # TODO once more auth groups are in, allow any admin or whatever to delete anything
    # till then, only owner might delete
    # This endpoint allows authorised users to delete a forslag
    # Requires an id in the query parameters
    @bugge.route("/forslag", "DELETE")
    def delete_forslag():
        cur_user_id = api_utils.get_cur_user_id(bugge, DB_wrap)
        if(cur_user_id == -1):
            bugge.respond_error("JSON", 403,
                                error_msg="The current user was not found in alias list")
            return

        query_params = parse_qs(bugge.env["QUERY_STRING"])
        # This endpoint does not make sense if id is not specified
        # The user does not get to delete the concept of a forslag
        if("id" not in query_params):
            bugge.respond_error("JSON", 422, error_msg="No id provided in query parameters")
            return

        forslag_id = query_params["id"][0] 
        # Now we must check the owner of the forslag
        owner_cursor = bugge.get_DB_cursor()
        owner_query = \
            """
            SELECT brukerid FROM forslag WHERE forslagid=%s
            """

        owner_cursor.execute(owner_query, [forslag_id])
        owner_result = owner_cursor.fetchone()

         # We only expect one result. Try catch just in case
        try:
            owner_cursor.close();
        except Exception:
            pass

        # If the requested forslag is not in database,
        # return a 200 as the end results of beeing removed and not beeing there are the same
        if(owner_result == None):
            bugge.respond_JSON(body={"id":forslag_id})
            return

        owner_result = owner_result[0] # unpack result id from tuple

        is_authorised = owner_result;
        # If the user is not the owner of the current forslag, check for general delete rights
        if(is_authorised == False):
            permissions = api_utils.get_permissions(cur_user_id, 'forslag', bugge)
            is_authorised = 'slette' in permissions

        if(is_authorised == False):
            bugge.respond_error("JSON", 403,
                                error_msg = \
                                ("Unauthorised to delete forslag with id " +
                                 forslag_id))
            return


        # Now we know the user is authorised to delete
        delete_query =\
            """
            DELETE FROM forslag WHERE forslagid=%s
            """


        # If this fails, the wrapping server will return a 500, don't think about it
        delete_cursor = bugge.get_DB_cursor()
        delete_cursor.execute(delete_query, [forslag_id])
        delete_cursor.close() # Should not contain anything

        # Commit change
        bugge.commit_DB()

        # Respond with success
        bugge.respond_JSON(body={"id":forslag_id})

def setup_GET(bugge):
    # Must support filtering what forslag is selected. Use query parameters for this
    # Recognised parameters:
    # sorter = <[dato|stemmer|kategori]>-<[asc|desc]>
    # kategorier = [<list>]
    # sok = <substreng>
    #
    # sok matches either header or body
    # A match in either means the forslag is included in the response
    @bugge.route("/forslag", "GET")
    def show_forslag():
        # First all parameters must be prepared
        # What user is currently logged on?
        cur_user_id = api_utils.get_cur_user_id(bugge, DB_wrap)
        if(cur_user_id == -1):
            bugge.respond_error("JSON", 403,
                                error_msg="The current user was not found in alias list")
            return

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
        valid_category_ids = api_utils.get_valid_category_ids(bugge)
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
        sok_value = "%" # by default, match all (in regex, this would be .*)
         # ILIKE means case insensetive match
        forslag_query_sok = " (tittel ILIKE %s OR forslag ILIKE %s) "
        if("sok" in query_dict):
            sok_param_value = query_dict["sok"][0]
            # As this is included in a prepared statement,
            # copying query string verbatim should be safe
            # the surrounding %% ensures it is matched wherever it is in the text
            sok_value = "%" + sok_param_value + "%"

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


        SQL_query_params = [cur_user_id, sok_value, sok_value]
        cursor.execute(forslag_query, SQL_query_params)

        # We must check this users general permissions for forslag
        permissions = api_utils.get_permissions(
            cur_user_id, 'forslag', bugge)

        row_count = 0
        rows = []
        for row in cursor:
            row_count += 1
            rows += [row]

        response = [{} for x in range(0, row_count)]
        row_count = 0
        for row in rows:
            forslag_user_id = row[4]
            cur_user_deleter = \
                (forslag_user_id == cur_user_id) \
                or "slette" in permissions
            cur_user_editor = "redigere" in permissions
            response[row_count] = {
                "forslagid": row[0],
                "tittel": row[1],
                "forslag": row[2],
                "lagt_til": str(row[3]),
                "statusid": row[5],
                "statusbeskrivelse": row[6],
                "num_reaksjoner": row[7],
                "cur_user_reacted": row[8],
                "cur_user_deleter": cur_user_deleter,
                "cur_user_editor": cur_user_editor
            }
            row_count += 1

        cursor.close()
        bugge.respond_JSON(response)
