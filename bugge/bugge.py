import json
import os

# The main purpose of this class is to abstract away the specific
# database handler used
# Support for
# connector/python: https://dev.mysql.com/doc/connector-python/en/
# Psycopg2: https://www.psycopg.org/docs/

# Both psycopg2 and connector/python follow the same general
# python database API (https://www.python.org/dev/peps/pep-0249/).
# This makes coding for both much easier, as the main differences
# will only be the name of the modules and SQL dialect differences
class DB_wrap:
    def __init__(self, config):
        self.load_config(config)
        self.connection = None

    def load_config(self, config):
        self.config = {
            "debug": False # Default value
        }
        # Obligatory fields
        try:
            self.config["dbname"] = config["dbname"]
            self.config["host"] = config["host"]
            self.config["pswd"] = config["pswd"]
            self.config["user"] = config["user"]
            self.config["dbtype"] = config["dbtype"]
            self.config["port"] = config["port"]
        except:
            raise Exception("Invalid config provided to DB_wrap")


    def connect(self):
        if(self.config == None):
            raise Exception("Attempted to fetch cursor before connecting database")
        
        # Default to mysql
        if "dbtype" not in self.config:
            self.config["dbtype"] = "mysql"
        
        if(self.config["dbtype"] == "mysql"):
            import mysql.connector
            self.connection = mysql.connector.connect(
                user = self.config["user"],
                database = self.config["dbname"],
                host = self.config["host"],
                password = self.config["pswd"]
            )
        elif(self.config["dbtype"] == "pg"):
            import psycopg2
            self.connection = psycopg2.connect(dbname=self.config["dbname"], user=self.config["user"], password=self.config["pswd"], host=self.config["host"],port=self.config["port"])
        else:
            raise Exception("Invalid database type " + self.config["dbtype"])
        
    def get_cursor(self):
        if(self.connection == None):
            raise Exception("Attempted to fetch cursor before connecting database")
        return self.connection.cursor()

    def close(self):
        if (self.connection is not None):
            self.connection.close()
            # As the connection is None again, the connect method might open a new connection
            self.connection = None
        
        
# Framework class
# Handles DB connection, routing, HTML and json response
class Bugge:
    def __init__(self):
        self.config_dict = None # None indicates the config file is not read
        self.env = None
        self.routes = {}
        self.DB = None # None indicates that no DB connection has been established
        self.url_params = {}

    # Python has destructors!
    # Ensures the DB connection is not left open
    def __del__(self):
        if(self.DB is not None):
            self.DB.close()
    
    def read_config(self, url):
        config_file_handle = open(url, 'r')
        config_file_lines = config_file_handle.readlines()
        config_dict = {}

        for line in config_file_lines:
            # Ignore empty lines and lines starting with "#" (comments)
            if(len(line) == 0 or line[0] == "#"):
                continue

            # Remove all spaces and tabs
            line = line.replace(' ', '').replace('\t', '')
            
            [key, value] = line.split("=")
            value = value.strip('\n')
            config_dict[key] = value
        
        config_file_handle.close()

        # Are we in debug mode?
        if "debug" in config_dict:
            if(config_dict["debug"].lower() == "true"):
                config_dict["debug"] = True
            else:
                config_dict["debug"] = False

        else:
            config_dict["debug"] = False # Debug is off by default

        self.config_dict = config_dict

    def read_environment(self):
        self.env = {} # Initalise empty dictionary
        if (self.config_dict["debug"] == True):
            from env import env 
            self.env = env
        else:
            # Apache does not provide PATH_INFO if the request is for the API root
            # Thus we need to make sure it exist before we try to read it
            if "PATH_INFO" in os.environ:
                self.env["PATH_INFO"] = os.environ["PATH_INFO"]
            else:
                self.env["PATH_INFO"] = "/"
                
            self.env["QUERY_STRING"] = os.environ["QUERY_STRING"]
            self.env["REMOTE_USER"] = os.environ["REMOTE_USER"]
            self.env["REQUEST_METHOD"] = os.environ["REQUEST_METHOD"]

    def get_config(self):
        if(self.config_dict is None):
            raise Exception("Config is not loaded")
        return self.config_dict

    ### Requests and routing
    # Decorator used to add route, to create a pattern resembeling flask
    def route(self, route, method):
        def decorator(route_handler):
            self.add_route(route_handler, route, method)
        return decorator

    # Internal route adder. The decorator wraps this method
    def add_route(self, handler, path, method):
        # Keyed by a concatenation of method and url
        # Only saves the handler function, not the context
        route_key = method + ":" + path
        self.routes[route_key] = handler
        
    def route_request(self, path, method):
        route_key = method + ":" + path

        if route_key in self.routes:
            self.routes[route_key](); # Execute handler function
        else:
            self.respond_error("HTML", 404) # Return a 404 not found in html format

    # Reads request paramters with read request, reads payload if the request is POST.
    # Uses the aquired input to handle the request and call the correct response.
    # Not sure what cases this will be able to cover, but a lot of cases should be possible to automate
    def handle_request(self):
        # Ensure environment is read
        if(self.env == None):
            self.read_environment()

        path = self.env["PATH_INFO"]
        method = self.env["REQUEST_METHOD"]
        self.route_request(path, method)

    ### DB methods
    def init_DB(self):
        if(self.config_dict == None):
            raise Exception("Bugge cannot connect to the DB before the config file is read, call read_config first")
        self.DB = DB_wrap(self.config_dict)
        self.DB.connect()

    def get_DB_cursor(self):
        if(self.DB == None):
            raise Exception("Database handler not initialised, init_DB must be run before any other DB actions")
        return self.DB.connection.cursor()


    ### Response handlers
    def respond_HTML(self, body, status=200):
        header = \
        "content-type: text/html\n" + \
        "status: " + str(status) + "\n\n"
            
        response = header + body
        print(response)

    # Only accepts strings and dicts as body for now
    def respond_JSON(self, body, status=200):
        # Comparision with the class objects of string and dictionary.
        # Seems to work fine, as the class objects should be unique?
        if(type(body) == str):
            pass

        elif(type(body) == dict or type(body) == list):
            body = json.dumps(body)

        else:
            respond_error("JSON", 500)
            return
        
        header = \
        "content-type: text/json\n" + \
        "status: " + str(status) + "\n\n"

        response = header + body
        print(response)


    def respond_error(self, type, error_code):
        if(type == "HTML"):
            self.respond_HTML("<h1>Error " + str(error_code) + "</h1>", status=error_code)

        if(type == "JSON"):
            self.respond_JSON({"http-error": error_code}, status=error_code)
