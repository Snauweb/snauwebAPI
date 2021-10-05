#!/usr/bin/python3

# Versjon 1 av snauwebs api
# Dette scriptet kjøres av apache når det requestes gjennom CGI
# CGI definerer en rekke headere som gir tilgang på brukernavn,
# requesttype, querystreng og mer. RFC 3875 definerer alle mulige
# headere, lenke: https://datatracker.ietf.org/doc/html/rfc3875

import os
user =  os.environ["REMOTE_USER"]
method = os.environ["REQUEST_METHOD"]
query_string = os.environ["QUERY_STRING"]

print("Content-type: text/html\n\n")
print("Hello, user " + user)
print("API queried with method " + method)
print("Query is " + query_string)
