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
       username VARCHAR(30),
       firstname VARCHAR(30)
);

-- Inserting the test user johalaf (kerberos alias "johanpålåfte")
INSERT INTO "tbl_User"
(userid, username, email, firstname, lastname, birthdate, tlf)
VALUES
(2, 'johalaf', 'johan@låfte.samfundet.no', 'johan', 'pålåfte', '01-01-1967', '0');

