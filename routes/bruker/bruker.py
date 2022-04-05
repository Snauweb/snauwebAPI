from urllib.parse import parse_qs

import sys
sys.path.append('../../')
import api_utils

def setup_routes(bugge):
    setup_GET(bugge)


def setup_GET(bugge):
    # As of now, any authenticated user is allowed to view the same user info
    # Accepts id as a query parameter. If more ids, pick first
    @bugge.route("/bruker", "GET")
    def get_brukerinfo():
        cursor = bugge.get_DB_cursor()
        query_dict = parse_qs(bugge.env["QUERY_STRING"])

        cur_user_is_editor = False
        cur_user_is_deleter = False
        cur_user_ID = api_utils.get_cur_user_id(bugge)
        cur_get_ID = -1;
        
        # Find ID of user to fetch info for
        # If id is specified in url, use it
        if "id" in query_dict:
            cur_get_ID = query_dict["id"][0]

        # Otherwise use the id of the currenty logged on user
        # In this case, the requesting user is allways editor
        else:
            cur_get_ID = cur_user_ID
            cur_user_is_editor = True
            
        # Check permissions
        user_permissions = api_utils.get_permissions(cur_user_ID, "bruker", bugge)

        if "redigere" in user_permissions:
            cur_user_is_editor = True

        if "slette" in user_permissions:
            cur_user_is_deleter = True
        
    
        query = """
        SELECT
        userid, username, email, firstname, lastname, birthdate, tlf, adres, study,
        active, altadres, webpage, begin, quit, comment, gmlsnau, otherinfo, nocontact,
        pnr, psted, country, confirmed, pensioned
        FROM "tbl_User"
        WHERE userid=%s;
        """

        cursor.execute(query, [cur_get_ID])

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
        # Include information about constraints for the editing frontend
        response = create_response_dict(result)

        # Add permissions 

        # Discard any items remaing in cursor. If any items do remain,
        # this will cause an exception. We ignore it.
        try:
            cursor.close();
        except Exception:
            pass

        bugge.respond_JSON(response)


def create_response_dict(result):
    email_max_length = 50
    firstname_max_length = 30
    lastname_max_length = 30
    tlf_max_length = 15
    adres_max_length = 100
    study_max_length = 40
    altadres_max_length = 100
    webpage_max_length = 100
    psted_max_length = 20
    country_max_length = 20
    
    result = {
        "id": {
            "verdi": result[0]
        },
        "brukernavn": {
            "verdi": result[1]
        },
        "epost": {
            "verdi": result[2],
            "makslengde": email_max_length,
            "type": "tekst"
        },
        "fornavn": {
            "verdi": result[3],
            "makslengde": firstname_max_length,
            "type": "tekst"
        },
        "etternavn": {
            "verdi": result[4],
            "makslengde": lastname_max_length,
            "type": "tekst"
        },
        "født": {
            "verdi": str(result[5]),
            "type": "dato"
        },
        "telefon": {
            "verdi": result[6],
            "makslengde": tlf_max_length,
            "type": "tekst"
        },
        "adresse": {
            "verdi": result[7],
            "makslengde": adres_max_length,
            "type": "tekst"
        },
        "studie": {
            "verdi": result[8],
            "makslengde": study_max_length,
            "type": "tekst"
        },
        "aktiv": {
            "verdi": result[9],
            "type": "bool"
        },
        "altadresse": {
            "verdi": result[10],
            "makslengde": altadres_max_length,
            "type": "tekst"
        },
        "nettsted": {
            "verdi": result[11],
            "makslengde": webpage_max_length,
            "type": "tekst"
        },
        "startet": {
            "verdi": str(result[12]),
            "type": "dato"
        },
        "sluttet": {
            "verdi": str(result[13]),
            "type": "dato"
        },
        "kommentar": {
            "verdi": result[14],
            "type": "tekst"
        },
        "gammelsnau": {
            "verdi": result[15],
            "type": "bool"
        },
        "ekstrainfo": {
            "verdi": result[16],
            "type": "tekst"
        },
        "ikkekontakt": {
            "verdi": result[17],
            "type": "bool"
        },
        "postnummer": {
            "verdi": result[18],
            "type": "tall"
        },
        "poststed": {
            "verdi": result[19],
            "makslengde": psted_max_length,
            "type": "tekst"
        },
        "land": {
            "verdi": result[20],
            "makslengde": country_max_length,
            "type": "tekst"
        },
        "bekrefta": {
            "verdi": str(result[21]),
            "type": "dato"
        },
        "pang": {
            "verdi": result[22],
            "type": "bool"
        }
    }

    return result
