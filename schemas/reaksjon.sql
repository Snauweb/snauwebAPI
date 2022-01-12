CREATE TABLE forslag_reaksjon (
       brukerid INTEGER REFERENCES "tbl_User"(userid)
       ON UPDATE CASCADE ON DELETE CASCADE,
       forslagid INTEGER REFERENCES "forslag"(forslagid)
       ON UPDATE CASCADE ON DELETE CASCADE,
       reaksjonstypeid INTEGER REFERENCES "reaksjonstype"(reaksjonstypeid)
       ON UPDATE CASCADE ON DELETE CASCADE
);

--- rows in forslag_reaksjon must be unique, we add an index constraint to make this happen
CREATE UNIQUE INDEX ON forslag_reaksjon (brukerid, forslagid, reaksjonstypeid);

CREATE TABLE reaksjonstype (
       reaksjonstypeid SERIAL PRIMARY KEY,
       beskrivelse VARCHAR(256) NOT NULL
);
