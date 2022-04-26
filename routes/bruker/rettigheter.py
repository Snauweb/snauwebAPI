import sys
sys.path.append('../../')
import api_utils

from urllib.parse import parse_qs

def setup_routes(bugge):
    setup_GET(bugge)

# Accepts parameters
# resurs = <ressursnavn1>([, <ressursnavn2>...])*
# id = <brukerid>
#
# If resurs is not specified, return permissions for all resources
# If id is not specified, return info for currently logged on user
def setup_GET(bugge):
    @bugge.route("/bruker/rettigheter", "GET")
    def get_rettigheter():
        cur_user_id = api_utils.get_cur_user_id(bugge)
        query_params = bugge.get_URL_parameters()
        
        # The two main parameters, set to defaults
        query_user = cur_user_id
        query_resources = [] # "match all"

        # If id is in the query parameters, use it rather than current user
        if "id" in query_params:
            query_user = query_params["id"][0]

        # A list of resources is provided
        if "resurs" in query_params:
            query_resources = \
                split_and_remove_chars(
                    query_params["resurs"][0],
                    removechars=" "
                )
            

            
        cursor = bugge.get_DB_cursor()

        query = create_rettigheter_query(query_resources)
        query_parameter_list = [query_user] + query_resources
        
        cursor.execute(query, query_parameter_list)
        response = {
            "userid": query_user
        }

        for row in cursor:
            resurs = row[0]
            handling = row[1]

            if (resurs not in response):
                response[resurs] = []

            response[resurs].append(handling)
        
        bugge.respond_JSON(response)

        cursor.close()


def split_and_remove_chars(string, splitchar=",", removechars=" "):
    result_string = ""
    for char in string:
        if char not in removechars:
            result_string += char

    result_string = result_string.split(splitchar)
    return result_string

def create_rettigheter_query(query_params):
    select_part = """ 
    SELECT resurs, handling
    FROM bruker_tilgangsgruppe
    INNER JOIN tilgangsgruppe USING(gruppeid)
    INNER JOIN tilgangsgruppe_tilgang USING(gruppeid)
    INNER JOIN tilgang USING(tilgangid)
    """

    where_id_part = """
    WHERE brukerid=%s
    """

    where_resurs_part = create_tuple_match_query_string(query_params)

    where_part = where_id_part + where_resurs_part

    group_part = """
    GROUP BY resurs, handling
    """

    full_query = select_part + where_part + group_part

    return full_query

def create_tuple_match_query_string(query_params):
    # If no specific resources are requested, no limitations are set
    if (query_params == []):
        return ""

    result_query_string = "AND resurs in ("

    for param in query_params:
        result_query_string += ("%s, ")

    # remove trailing comma and space (last two characters)
    result_query_string = result_query_string[:-2]
    
    result_query_string += ")"

    return result_query_string
