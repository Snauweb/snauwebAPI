#!/usr/bin/python3

# Versjon 1 av snauwebs api
# Dette scriptet kjøres av apache når det requestes gjennom CGI
# CGI definerer en rekke headere som gir tilgang på brukernavn,
# requesttype, querystreng og mer. RFC 3875 definerer alle mulige
# headere, lenke: https://datatracker.ietf.org/doc/html/rfc3875

import os
credentials_file_location = "../../credentials/db.txt"


def setup_env_vars(vars_dict):
    vars_dict["user"] =  os.environ["REMOTE_USER"]
    vars_dict["method"] = os.environ["REQUEST_METHOD"]
    vars_dict["query_string"] = os.environ["QUERY_STRING"]
    try:
        vars_dict["path"] = os.environ["PATH_INFO"]
    except Exception:
        vars_dict["path"] = ""

def get_db_credentials(credentials_dict):
    pass
    
    
def main():
    vars_dict = {};
    setup_env_vars(vars_dict)
    
    print("Content-type: text/json")
    print("Status: 204 NO CONTENT\n\n")
    print("{ \n")
    print("\"user\": \"" + vars_dict["user"] + "\",\n")
    print("\"method\": \"" + vars_dict["method"] + "\",\n")
    print("\"queryString\": \"" + vars_dict["query_string"] + "\",\n")
    print("\"path\": \"" + vars_dict["path"] + "\"\n")
    print("}")
    
# Only run as script
if (__name__ == "__main__"):
    main()
