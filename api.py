#!/usr/bin/python
# -*- coding: utf-8 -*-

# Versjon 1 av snauwebs api
# Dette scriptet kjøres av apache når det requestes gjennom CGI
# CGI definerer en rekke headere som gir tilgang på brukernavn,
# requesttype, querystreng og mer. RFC 3875 definerer alle mulige
# headere, lenke: https://datatracker.ietf.org/doc/html/rfc3875
import os
DEBUG = True;

# We assume all inputs and files are in order
# if not it crashes and burns
def read_config(config_dict, config_location):

    config_file_handle = open(config_location, 'r')
    config_file_lines = config_file_handle.readlines()

    for line in config_file_lines:
        [key, value] = line.split("=")
        value = value.strip('\n')
        config_dict[key] = value;


def connect_to_db(dbtype):
    if(dbtype == "PG"):
        pass
    elif(dbtype == "MYSQL"):
        pass
    else:
        raise Exception("Non supported DB type " + dbtype + " provided, aborting...")

def main():

    # contains DB type and credentials
    config_dict = {}
    if(DEBUG == False):
        user =  os.environ["REMOTE_USER"]
        method = os.environ["REQUEST_METHOD"]
        query_string = os.environ["QUERY_STRING"]

        print("Content-type: text/html\n\n")
        print("Hello, user " + user)
        print("API queried with method " + method)
        print("Query is " + query_string)

    if(DEBUG == True):
        read_config(config_dict, "../../configs/config.txt")
        print(config_dict)

    DB_handle = connect_to_db(config_dict["dbtype"]);

if(__name__ == "__main__"):
    main()
else:
    print("a module?")
