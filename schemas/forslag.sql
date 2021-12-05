-- Forslag til snauweb går i denna

CREATE TABLE forslag (
       id SERIAL PRIMARY KEY,
       tittel VARCHAR(256) NOT NULL,
       forslag TEXT NOT NULL,
       lagt_til TIMESTAMP WITHOUT TIME ZONE,
       brukerid INTEGER REFERENCES "tbl_User"(userid)		
);
