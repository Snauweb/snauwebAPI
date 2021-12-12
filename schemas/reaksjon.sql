CREATE TABLE forslag_reaksjon (
       brukerid INTEGER REFERENCES "tbl_User"(userid),
       forslagid INTEGER REFERENCES "forslag"(forslagid),
       reaksjonstypeid INTEGER REFERENCES "reaksjonstype" (reaksjonstypeid)
);

CREATE TABLE reaksjonstype (
       reaksjonstypeid SERIAL PRIMARY KEY,
       beskrivelse VARCHAR(256) NOT NULL
);
