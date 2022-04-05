-- Contains sql related to user tables


-- *** TABLE CREATION ***

-- Orignial user schema


-- A given user ID can have any number of aliases (in praxis it will be only old and ITK)
-- To maintain compatability between new and old system,
-- any alias should be translated into its corresponding ID before use

-- Old user names have a character limit of 30.
-- The usernames are authenticated through Kerberos are controlled by ITK.
-- 100 chars should be a reasonable upper limit
CREATE TABLE brukeralias (
       id SERIAL PRIMARY KEY,
       brukerid INTEGER NOT NULL references "tbl_User"(userid) ON UPDATE CASCADE ON DELETE CASCADE,
       brukeralias VARCHAR(100) NOT NULL UNIQUE
);

-- ONLY FOR TESTING
CREATE TABLE "tbl_User" (
       userid SERIAL PRIMARY KEY,
       username VARCHAR(30) DEFAULT NULL,
       email VARCHAR(50) DEFAULT NULL,
       firstname VARCHAR(30) DEFAULT NULL,
       lastname VARCHAR(30) DEFAULT NULL,
       birthdate DATE,
       tlf VARCHAR(15),
       adres VARCHAR(100) DEFAULT NULL,
       study VARCHAR(40) DEFAULT NULL,
       pass  VARCHAR(32) DEFAULT NULL,
       active BOOLEAN,
       altadres VARCHAR(100),
       webpage VARCHAR(100),
       begin DATE,
       quit DATE,
       comment TEXT,
       gmlsnau BOOLEAN DEFAULT FALSE,
       otherinfo TEXT,
       nocontact BOOLEAN DEFAULT FALSE,
       member BIGINT,
       gjengmember BIGINT,
       ukamember BIGINT,
       pnr INTEGER DEFAULT 0,
       psted VARCHAR(20),
       country VARCHAR(20),
       confirmed TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
       pensioned BOOLEAN DEFAULT FALSE
);

-- Inserting the test user johalaf (kerberos alias "johanpålåfte")
INSERT INTO "tbl_User"
(userid, username, email, firstname, lastname, birthdate, tlf)
VALUES
(2, 'johalaf', 'johan@låfte.samfundet.no', 'johan', 'pålåfte', '01-01-1967', '0');

-- Selecting all info for user with id=2
SELECT
userid, username, email, firstname, lastname, birthdate, tlf, adres, study,
active, altadres, webpage, begin, quit, comment, gmlsnau, otherinfo, nocontact,
pnr, psted, country, confirmed, pensioned
FROM "tbl_User"
WHERE userid=2;
