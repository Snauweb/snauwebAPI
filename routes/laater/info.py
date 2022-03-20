def setup_routes(bugge):
    setup_get(bugge)

# Returns names, descriptions, genere and id of the requested laat
def setup_get(bugge):
    @bugge.route("/laater/info", "GET")
    def get_laat_info():
        query_dict = parse_qs(bugge.env["QUERY_STRING"])

        # No id specified is an error
        if("id" not in query_dict):
            bugge.respond_error("JSON", 422,
                                error_msg="Must specify what låt to show info for")
            return


        cur_id = query_dict["id"][0]

        nickname_cursor = bugge.get_DB_cursor();
        laat_info_cursor = bugge.get_DB_cursor();

        nickname_query="""
        SELECT name, description 
        FROM "tbl_Nickname" 
        WHERE melid = %s
        ORDER BY name ASC
        """

        nickname_cursor.execute(nickname_query, [cur_id])

        names = []
        descriptions = []
        for result in nickname_cursor:
            names.append(result[0])
            descriptions.append(result[1])


        laat_info_query = """
        SELECT dansid, description 
        FROM "tbl_Melody"
        WHERE melid = %s
        """

        laat_info_cursor.execute(laat_info_query, [cur_id])
        dansid = "usortert"

        found_laat = False
    
        for result in laat_info_cursor:
            descriptions.insert(0, result[1]) #put description from melid at the front
            dansid = result[0]
            found_laat = True


        nickname_cursor.close()
        laat_info_cursor.close()

        if (found_laat == False):
            bugge.respond_error("JSON", 404,
                                error_msg="No låt with id " + cur_id + " found")
            return
    
        response = {
            "id": cur_id,
            "navn": names,
            "beskrivelser": descriptions,
            "sjanger": dansid
        }
    
 
        bugge.respond_JSON(response)
    

