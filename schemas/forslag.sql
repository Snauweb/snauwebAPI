-- Forslag til snauweb går i denna

CREATE TABLE forslag (
       forslagid SERIAL PRIMARY KEY,
       tittel VARCHAR(256) NOT NULL,
       forslag TEXT NOT NULL,
       lagt_til TIMESTAMP WITHOUT TIME ZONE,
       brukerid INTEGER REFERENCES "tbl_User"(userid),
       statusid INTEGER REFERENCES "forslagstatus"(statusid)
       
);


CREATE TABLE forslagstatus (
       statusid SERIAL PRIMARY KEY,
       beskrivelse VARCHAR(30) NOT NULL
);


