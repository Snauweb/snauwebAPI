import json
import sys

from bugge.bugge import Bugge
from bugge.bugge import DB_wrap

bugge = Bugge()
bugge.read_config("./.config")
bugge.init_DB()
cursor = bugge.get_DB_cursor()
cursor.execute("select * from forslag")
for row in cursor:
    print(row)

""" def db(databaseName='d77uck12p6lknh'):
    return psycopg2.connect(database=databaseName)

def query_db(query, args=(), one=False):
    cur = db().cursor()
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value)
        for i, value in enumerate(row)) for row in cur.fetchall()]

    cur.connection.close()
    return (r[0] if r else None) if one else r

my_query = query_db("select * from majorroadstiger limit %s", (3,))

json_output = json.dumps(my_query) """


