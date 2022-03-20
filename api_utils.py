#!/usr/bin/python3

from urllib.parse import parse_qs

# Get user permissions for a resource
# Returns a list of all permitted actions on the given resouce for the given user
def get_permissions(userid, resource_name, bugge):
    query = \
        """
        SELECT handling
        FROM bruker_tilgangsgruppe
        INNER JOIN tilgangsgruppe USING(gruppeid)
        INNER JOIN tilgangsgruppe_tilgang USING(gruppeid)
        INNER JOIN tilgang USING(tilgangid)
        WHERE brukerid=2 and resurs='forslag'
        GROUP BY handling
        """

    result = []
    
    with bugge.get_DB_cursor() as cursor:
        cursor.execute(query, [userid, resource_name])
        for result_row in cursor:
            result.append(result_row[0])

    return result

# Get a list of valid kategori ids
def get_valid_category_ids(bugge):
    cursor = bugge.get_DB_cursor()
    query = \
        """
        SELECT statusid FROM forslagstatus
        """

    cursor.execute(query)
    
    result_list = []
    for result in cursor:
        result_list += result

    cursor.close()
    return result_list

    

# Get number of reactions for all ids in parameter
def get_single_reaction_count(forslagid, userid, bugge, dbwrap):
    reaction_cursor = bugge.get_DB_cursor()
    reaction_query = \
        """
        SELECT count(*) AS num_reaksjoner, bool_or(brukerid=%s) AS cur_user_reacted
        FROM forslag_reaksjon 
        WHERE forslagid=%s
        GROUP BY forslagid;
        """
        
     
    reaction_cursor.execute(reaction_query, [userid, forslagid])
    
    result = reaction_cursor.fetchone();
    reaction_cursor.close();

    return result

def get_all_reaction_counts(userid, bugge, dbwrap):
    reaction_cursor = bugge.get_DB_cursor()

    reaction_query = \
        """
            SELECT forslagid, 
                   count(*) AS num_reaksjoner, 
                   bool_or(brukerid=%s) AS cur_user_reacted
            FROM forslag_reaksjon 
            GROUP BY forslagid;
        """

    reaction_cursor.execute(reaction_query, [userid])
        

    total_rows = 0
    rows = []
    for row in reaction_cursor:
        total_rows += 1
        rows += [row]

    return rows


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

    # If the user is not found, it's an indication of some larger problem
    # Still, the api should not crash just because this is the case
    if(result == None):
        return -1
    else:
        return result[0]
