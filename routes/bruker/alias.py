def setup_routes(bugge):
    setup_GET(bugge)

def setup_GET(bugge):
    # Shows all active aliases
    @bugge.route("/bruker/alias", "GET")
    def get_active_aliases():
        cursor = bugge.get_DB_cursor()

        query = """
        SELECT username, brukeralias FROM
        (SELECT userid, username from "tbl_User") AS u
        INNER JOIN brukeralias AS b ON u.userid = b.brukerid
        """

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
