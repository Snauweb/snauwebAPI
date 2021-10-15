# Abstracts the driver away from users, making it easier to switch between
# production and testing

# Pre-baked SQL
CREATE_SUGGESTION_TABLE = '\
CREATE TABLE suggestion (\
id int(20) NOT NULL AUTO_INCREMENT,\
username varchar(50),\
text_body text,\
PRIMARY KEY (id)\
)\
'

class DB_handler:
    def __init__(self, config_dict):
        self.dbtype = config_dict["dbtype"]
        self.user = config_dict["user"]
        self.password = config_dict["pswd"]
        self.dbname = config_dict["dbname"]
        self.host = config_dict["host"]
        # Any DB operations on the object are illegal when this is false
        self.connected = False

    # Connection decorator (implemented as a static method for simplicity)
    # (https://pythonbasics.org/decorators/)
    # (https://www.artima.com/weblogs/viewpost.jsp?thread=240845#decorator-functions-with-decorator-arguments)
    def require_connected(func):
        def connected_check(self, *args): #Can handle an arbitrary number of arguments
            if(self.connected == False):
                raise Exception("No DB operations are permitted before connection to DB")
            func(self, *args)

        return connected_check
        
        
        
    # **** DB utils ****
    # After this method, the table wih name <tbl_name> is guaranteed to exist
    @require_connected
    def ensure_exist(self, tbl_name):
        if(self.dbtype == "PG"):
            pass
        elif(self.dbtype == "MYSQL"):
            try:
                self.cursor.execute(CREATE_SUGGESTION_TABLE)
            except Exception as error:
                # The only acceptable error is Table exists error
                # Any other exceptions are passed on
                if(error.errno != 1050):
                    raise error
                        
    # Accepts the name of the table to append
    @require_connected
    def appendToTable(self, table_name, rows):
        if(table_name == "suggestion"):
            self.ensure_exist("suggestion")
            # Use the template syntax to sanitise the input.
            # If you construct queries manually, then you've got to sanitise yourself!
            query = (
                "INSERT INTO suggestion (`username`, `text_body`)" +
                "values(%s, %s )"
            )
            self.cursor.execute(query, rows)
            
    def connect(self):
        if(self.connected == True):
            raise Exception("Tried to connect an already connected DB_handler")
        
        if(self.dbtype == "PG"):
            pass ## Connect with psycopg2

        elif(self.dbtype == "MYSQL"):
            import mysql.connector
            from mysql.connector import errorcode
            
            # No exception handeling for now,
            # if the connection fails we might as well crash
            self.handle = mysql.connector.connect(
                user=self.user,
                database=self.dbname,
                password=self.password,
                host=self.host
            )
            self.cursor = self.handle.cursor()
            self.cursor.execute("USE {}".format(self.dbname))
            self.connected = True


    @require_connected
    def disconnect(self):
        if(self.dbtype == "PG"):
            pass
        elif(self.dbtype == "MYSQL"):
            self.handle.close()
            
