# Returnerer informasjon om lydopptak
from urllib.parse import parse_qs


def setup_routes(bugge):
    setup_get(bugge)
    
    
def setup_get(bugge):
    @bugge.route("/laater/recordings", "GET")
    def get_laat_recording():
        query_param_dict = parse_qs(bugge.env["QUERY_STRING"])
        if ("id" not in query_param_dict):
            bugge.respond_error("JSON", 422,
                                error_msg="Must specify what låt to show recordings for")
            return
        
        requested_id = query_param_dict["id"][0]
        
        cursor = bugge.get_DB_cursor();
        query="""
        SELECT recid, filename, description
        FROM "tbl_mel_rec" INNER JOIN "tbl_Recording" USING (recid)
        WHERE melid=%s;  
        """

        cursor.execute(query, [requested_id])

        response = {
            "melid": requested_id,
            "recordings": []
        }
    
        for row in cursor:
            data_object = {
                "id": row[0],
                "filnavn": row[1],
                "beskrivelse": row[2]
            }

            response["recordings"].append(data_object)
            
        cursor.close()
        bugge.respond_JSON(response)
