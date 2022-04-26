#!/usr/bin/python3

import json
import psycopg2
import sys
import os
import datetime
from urllib.parse import parse_qs

from bugge.bugge import Bugge
from bugge.bugge import DB_wrap

import api_utils

# Import routes
import routes.laater

import routes.laater.recordings
import routes.laater.sheetmusic
import routes.laater.info

import routes.reaksjon

import routes.bruker
import routes.bruker.alias
import routes.bruker.rettigheter

import routes.forslag

# API framework class
bugge = Bugge()

# If configLocation file exists, use it. Otherwise use hard coded default
configPath = "../configs/config.txt" # <- Default
try:
    from configLocation import configLocation
    configPath = configLocation

# if no file exists python will get mad. Catch the excption here with a noop
# This makes the framework fall back to the defult defined above
except: 
    pass

bugge.read_config(configPath)
bugge.init_DB()


# Route setup. Package structure REALLY SHOULD match url hierarchy!
# *********** Låter ***********

routes.laater.setup_routes(bugge)

routes.laater.recordings.setup_routes(bugge)
routes.laater.sheetmusic.setup_routes(bugge)
routes.laater.info.setup_routes(bugge)


# *********** REAKSJON ***********
routes.reaksjon.setup_routes(bugge)
        

# *********** ALIAS ***********
routes.bruker.alias.setup_routes(bugge)    

# *********** BRUKER ***********
routes.bruker.setup_routes(bugge)

# *********** RETTIGHETER ************
routes.bruker.rettigheter.setup_routes(bugge)


# *********** FORSLAG ***********
routes.forslag.setup_routes(bugge)



# The api root should contain instructions for api use
@bugge.route("/", "GET")
def show_help():
    bugge.respond_HTML("<h1>Snauweb API</h1> <p>Her burde det stå instruksjoner for API-bruk")

# Reads the request from
# env.py if in debug,
# os.environ if not in debug (deploy)
bugge.handle_request()
