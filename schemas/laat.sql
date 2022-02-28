CREATE TABLE "tbl_Dans" (
       dansid VARCHAR(20) PRIMARY KEY,
       description text NOT NULL
);

CREATE TABLE "tbl_Melody" (
       melid SERIAL PRIMARY KEY,
       dansid VARCHAR(20) NOT NULL DEFAULT 'usortert' REFERENCES "tbl_Dans"(dansid) ON UPDATE CASCADE ON DELETE CASCADE,
       description TEXT NOT NULL
);

CREATE TABLE "tbl_Nickname" (
       nickid SERIAL PRIMARY KEY,
       melid INTEGER NOT NULL REFERENCES "tbl_Melody"(melid) ON UPDATE CASCADE ON DELETE CASCADE,
       name VARCHAR(50) NOT NULL,
       description TEXT NOT NULL
);




-- Eksempelspørringer
-- For å hente id, navn og dans for alle låter i alfabetisk rekkefølge
SELECT melid, name, dansid
FROM "tbl_Melody" LEFT JOIN "tbl_Nickname" USING (melid)
ORDER BY name ASC;

