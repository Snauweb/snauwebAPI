#!/usr/bin/python3

from urllib.parse import parse_qs


# Contains helper functions for the main api endpoint

# To check for database existence
# TODO
def is_id_in_db(table, idcol):
    pass

# For field validation
# Is this string a positive non 0 integer
def is_valid_id(string):
    try:
        string_as_int = int(string)
        if(string_as_int > 0):
            return True
        return False
    except:
        return False
            
# Id of user currently logged on
def get_cur_user_id(bugge, dbwrap):
    cursor = bugge.get_DB_cursor()

    user = bugge.env["REMOTE_USER"]
    # prune all the realm info from the name if needed
    # johan@AD.SAMFUNDET.NO -> johan
    if(not user.find('@') == -1):
        user = user[:user.find('@')]

    # Translate alias user name (from kerberos auth) into user_id,
    # use id to look up more user info
    query = \
        """ 
        SELECT brukerid FROM brukeralias where brukeralias.brukeralias = %s
        """
        
    cursor.execute(query, [user]);
    
    result = cursor.fetchone();


    # Discard any items remaing in cursor. If any items do remain,
    # this will cause an exception. We ignore it.
    try:
        cursor.close();
    except Exception:
        pass

    return result[0]
