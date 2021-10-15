#!/usr/bin/python
# -*- coding: utf-8 -*-

# Versjon 1 av snauwebs api
# Dette scriptet kjøres av apache når det requestes gjennom CGI
# CGI definerer en rekke headere som gir tilgang på brukernavn,
# requesttype, querystreng og mer. RFC 3875 definerer alle mulige
# headere, lenke: https://datatracker.ietf.org/doc/html/rfc3875
import os
from db_handler import DB_handler

# The debug flag can be overridden by the config file
DEBUG = False
CONFIG_FILE_LOCATION = "../../configs/config.txt"

# We assume all inputs and files are in order
# if not it crashes and burns
def read_config(config_dict, config_location):

    config_file_handle = open(config_location, 'r')
    config_file_lines = config_file_handle.readlines()

    for line in config_file_lines:
        [key, value] = line.split("=")
        value = value.strip('\n')
        config_dict[key] = value;

    print("debug" in config_dict)
    if("debug" in config_dict):
        global DEBUG # Tell python we want to update the global variable DEBUG
        if(config_dict["debug"] == "true"):
            DEBUG = True;
        else:
            DEBUG = False;
        
# Dummy env_vars in case of debug
def read_env_vars(env_var_dict):
    if(DEBUG):
        env_var_dict["REMOTE_USER"] = "testuser"
        env_var_dict["REQUEST_METHOD"] = "POST"
        env_var_dict["QUERY_STRING"] = ""
        env_var_dict["PATH_INFO"] = "/suggestions"

def read_payload():
    if(DEBUG):
        return "Mer alpakkaer takk'); DROP TABLE suggestion;"

# Messy solution, consider using Flask to help with this eventually
# Maybe make own decorators for more elegant wrapping?
def route(url, method, payload, dbho, env_var_dict):
    if(url == "/suggestions"):
        if(method == "GET"):
            print("GET!")
        elif(method == "POST"):
            print("POST!")
            dbho.appendToTable("suggestion",
                               [
                                   env_var_dict["REMOTE_USER"],
                                   payload
                               ])
        else:
            raise Exception("Invalid method " + method + " at URL " + url)
    
def main():
    config_dict = {} # Contains DB type, debug toggle and  credentials
    env_var_dict = {} # Request type, user name etc
    payload = "" # For POST requsts
    
    read_config(config_dict, CONFIG_FILE_LOCATION)
    print(config_dict)
    
    read_env_vars(env_var_dict)
    print(env_var_dict)

    payload = read_payload()
    print(payload)

    db_handler_object = DB_handler(config_dict)

    db_handler_object.connect();
    
    route(env_var_dict["PATH_INFO"],
          env_var_dict["REQUEST_METHOD"],
          payload,
          db_handler_object,
          env_var_dict)
    
    db_handler_object.disconnect();
    

if(__name__ == "__main__"):
    main()
else:
    print("api script launced as module, launch it as a script instead")
