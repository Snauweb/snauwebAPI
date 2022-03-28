from urllib.parse import parse_qs

def setup_routes(bugge):
    setup_get(bugge)


def setup_get(bugge):
     @bugge.route("/laater/sheetmusic", "GET")
     def get_laat_sheetmusic():

         query_param_dict = parse_qs(bugge.env["QUERY_STRING"])
         if ("id" not in query_param_dict):
             bugge.respond_error("JSON", 422,
                                 error_msg="Must specify what låt to show sheetmusic for")
             return
         
         requested_id = query_param_dict["id"][0]
         
         cursor = bugge.get_DB_cursor()
         
         query="""
         SELECT sheetid, filename, description
         FROM "tbl_Sheetmusic" INNER JOIN "tbl_mel_sheet" USING (sheetid)
         WHERE melid=%s
         """

         response = {
             "id": requested_id,
             "sheets": []
         }
         
         cursor.execute(query, [requested_id]);
         for result in cursor:
             response["sheets"].append({
                 "id": result[0],
                 "filnavn": result[1],
                 "beskrivelse": result[2],
                 "format": "pdf"
             })
         
         cursor.close()

         import sys
         print(response, file=sys.stderr)
         bugge.respond_JSON(response)
    
