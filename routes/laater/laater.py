def setup_routes(bugge):
    setup_get(bugge)

def setup_get(bugge):
    @bugge.route("/laater", "GET")
    def get_laater():
        cursor = bugge.get_DB_cursor();

        laater_query = """
        SELECT melid, name, dansid
        FROM "tbl_Melody" LEFT JOIN "tbl_Nickname" USING (melid)
        ORDER BY name ASC;
        """

        cursor.execute(laater_query)
    
        response = []

        for row in cursor:
            response.append({
                "id": row[0],
                "navn": row[1],
                "sjanger": row[2]
            })
    
        cursor.close()

        bugge.respond_JSON(response)


