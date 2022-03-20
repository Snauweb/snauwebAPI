def setup_routes(bugge):
    setup_get(bugge)


def setup_get(bugge):
     @bugge.route("/laater/sheetmusic", "GET")
     def get_laat_sheetmusic():
         cursor = bugge.get_DB_cursor();
         query="""

         """
         response = []
         cursor.close()
         bugge.respond_JSON(response)
    
