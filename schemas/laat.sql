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

CREATE TABLE "tbl_Recording" (
       recid SERIAL PRIMARY KEY,
       filename varchar(50) NOT NULL,
       description TEXT NOT NULL
);

CREATE TABLE "tbl_mel_rec" (
       melid INTEGER NOT NULL REFERENCES "tbl_Melody"(melid)
       ON UPDATE CASCADE ON DELETE CASCADE,
       recid INTEGER NOT NULL REFERENCES "tbl_Recording"(recid)
       ON UPDATE CASCADE ON DELETE CASCADE
);


-- Eksempelspørringer
-- For å hente id, navn og dans for alle låter i alfabetisk rekkefølge
SELECT melid, name, dansid
FROM "tbl_Melody" LEFT JOIN "tbl_Nickname" USING (melid)
ORDER BY name ASC;

-- For å hente alle opptak for melodien med id 1
SELECT melid, recid, filename, description
FROM "tbl_mel_rec" INNER JOIN "tbl_Recording" USING (recid)
WHERE melid = 1;  
