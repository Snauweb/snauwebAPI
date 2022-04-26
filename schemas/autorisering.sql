-- Consider adding cascading to updates/deletes here at some point
-- However, access and accessgroups should probably stay pretty fixed
-- This setup is designed to minimise redundancy of data, at the cost
-- of more table joins each lookup


-- The only way a user should be given a tilgang is through a tilgangsgruppe
CREATE TABLE tilgangsgruppe (
       gruppeid SERIAL PRIMARY KEY,
       gruppenavn VARCHAR(50) NOT NULL,
       beskrivelse VARCHAR(100) NOT NULL
);

-- We try to keep permissions resource based.
-- handling can be create, read, edit, or anything else that seems relevant
-- Yes, 'resurs' is a valid spelling in both NN and NB
CREATE TABLE tilgang (
       tilgangid SERIAL PRIMARY KEY,
       resurs VARCHAR(50),
       handling VARCHAR(50)
);
-- There should be no duplicate (resurs, handling)-pairs
CREATE UNIQUE INDEX ON tilgang(resurs, handling);

CREATE TABLE bruker_tilgangsgruppe (
       brukerid INTEGER NOT NULL REFERENCES "tbl_User"(userid),
       gruppeid INTEGER NOT NULL REFERENCES "tilgangsgruppe"(gruppeid)
);


-- To ensure a given group have only one set of permissions
-- for one resource, (gruppeid, ressurs) must be unique
CREATE TABLE tilgangsgruppe_tilgang (
       gruppeid INTEGER NOT NULL REFERENCES "tilgangsgruppe"(gruppeid),
       tilgangid INTEGER NOT NULL REFERENCES "tilgang"(tilgangid)
);

-- Enforce that a single group can only be connected
-- to a single tilgang once
CREATE UNIQUE INDEX ON tilgangsgruppe_tilgang(gruppeid, tilgangid);

-- Example permissions query, for user 2 and resource 'forslag'
-- Returns one row per action.
-- Group by clause may or may not be needed, it is to avoid
-- finding duplicate permissions for users that are part of
-- multiple groups

SELECT handling
FROM bruker_tilgangsgruppe
INNER JOIN tilgangsgruppe USING(gruppeid)
INNER JOIN tilgangsgruppe_tilgang USING(gruppeid)
INNER JOIN tilgang USING(tilgangid)
WHERE brukerid=2 and resurs='forslag'
GROUP BY handling;

-- Example query for user of id 2 and all permissions for several resources
SELECT resurs, handling
FROM bruker_tilgangsgruppe
INNER JOIN tilgangsgruppe USING(gruppeid)
INNER JOIN tilgangsgruppe_tilgang USING(gruppeid)
INNER JOIN tilgang USING(tilgangid)
WHERE brukerid=2 and resurs in ('forslag', 'bruker')
GROUP BY resurs, handling;
