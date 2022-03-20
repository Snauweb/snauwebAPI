
from urllib.parse import parse_qs

def setup_routes(bugge):
    setup_GET(bugge)


def setup_GET(bugge):
    # As of now, any authenticated user is allowed to view the same user info
    # Accepts id as a query parameter. If more ids, pick first
    @bugge.route("/bruker", "GET")
    def get_brukerinfo():
        cursor = bugge.get_DB_cursor()
        query_dict = parse_qs(bugge.env["QUERY_STRING"])

        # Dig up specified user data when requested by id
        if "id" in query_dict:
            query = \
                'SELECT username, firstname, lastname FROM \
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
                'SELECT username, firstname, lastname FROM \
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

