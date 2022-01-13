-- Consider adding cascading to updates/deletes here at some point
-- However, access and accessgroups should probably stay pretty fixed

CREATE TABLE tilgangsgruppe (
       gruppeid SERIAL PRIMARY KEY,
       gruppenavn VARCHAR(50) NOT NULL,
       beskrivelse VARCHAR(100) NOT NULL
);


CREATE TABLE bruker_tilgangsgruppe (
       brukerid INTEGER NOT NULL REFERENCES "tbl_User"(userid),
       gruppeid INTEGER NOT NULL REFERENCES "tilgangsgruppe"(gruppeid)
);

-- We try to keep permissions resource based.
-- create, read, edit, delete
-- Yes, 'resurs' is a valid spelling in both NN and NB
-- As a rule, any resource upploaded by a user should be deletable
-- by that user. To ensure a given group have only one set of permissions
-- for one resource, (gruppeid, ressurs) must be unique
CREATE TABLE tilgangsgruppe_tilgang (
       gruppeid INTEGER NOT NULL REFERENCES "tilgangsgruppe"(gruppeid),
       resurs VARCHAR(50),
       opprette BOOLEAN DEFAULT FALSE NOT NULL,
       lese BOOLEAN DEFAULT FALSE NOT NULL,
       redigere BOOLEAN DEFAULT FALSE NOT NULL,
       slette BOOLEAN DEFAULT FALSE NOT NULL
);

-- Enforce that a single group can only be connected
-- to a single set of resource permissions
CREATE UNIQUE INDEX ON tilgangsgruppe_tilgang(gruppeid, resurs);

-- Example permissions query, for user 2 and resource 'forslag'
-- Sometimes, the user might belong to multiple gropus.
-- To keep the result to one row, we group all rows by resurs
-- and use bool_or to merge the permission values

SELECT resurs, bool_or(opprette) as opprette,
bool_or(lese) as lese, bool_or(redigere) as redigere, bool_or(slette) as slette
FROM bruker_tilgangsgruppe
INNER JOIN tilgangsgruppe USING(gruppeid)
INNER JOIN tilgangsgruppe_tilgang USING(gruppeid)
WHERE brukerid=2 and resurs='forslag'
GROUP BY resurs;
