--Views
DROP VIEW IF EXISTS gamesbychampion;
CREATE VIEW gamesbychampion
AS
    SELECT a.*, COALESCE(b.nwins, 0) as wins, COALESCE(c.nlosses, 0) as losses
    FROM (SELECT cname
        FROM champions
) a
        FULL OUTER JOIN
        (SELECT P.champion, COUNT(*) as nwins
        FROM players P, playedin G
        WHERE P.playername = G.summonername AND outcome='win'
        GROUP BY P.champion) b
        ON a.cname=b.champion
        FULL OUTER JOIN
        (SELECT P.champion, COUNT(*) as nlosses
        FROM players P, playedin G
        WHERE P.playername = G.summonername AND outcome='loss'
        GROUP BY P.champion) c
        ON a.cname=c.champion
    ORDER BY wins DESC, losses, a.cname;

DROP VIEW IF EXISTS intournamentusers;
CREATE VIEW intournamentusers
AS
    SELECT a.summonername, a.squad, d.tourid, d.prizes, d.type, c.tplace
    FROM (
SELECT summonername, squad
        FROM users
) a
        JOIN (
SELECT u.squad, s.sqname
        FROM users u, squads s
        WHERE u.squad=s.sqname
        GROUP BY u.squad, s.sqname
) b
        ON a.squad=b.sqname
        JOIN (
SELECT s.sqname, ci.squad, ci.tplace, ci.tourid
        FROM squads s, competesIn ci
        WHERE S.sqname=ci.squad
        GROUP BY s.sqname, ci.squad, ci.tplace, ci.tourid) c
        ON b.sqname=c.squad
        JOIN
        (SELECT ci.tourid, t.prizes, t.type
        FROM competesin ci, tournaments t
        WHERE t.tourid=ci.tourid
        GROUP BY ci.tourid, t.type, t.prizes) d
        ON d.tourid=c.tourid
    ORDER BY a.summonername, d.tourid;

--Indexes
DROP INDEX IF EXISTS timestamp;
CREATE INDEX timestamp ON gameInstances(tstamp);

DROP INDEX IF EXISTS userrank;
CREATE INDEX userrank ON users(rank);

--Stored procedure
DROP FUNCTION IF EXISTS holidayGift
(INT, INT);
CREATE OR REPLACE FUNCTION holidayGift
(p_rank INT, p_money INT) RETURNS void AS
$$
DECLARE
unownedChampion text;
c_user CURSOR FOR
SELECT summonername, rank, money
FROM users;
c_id text;
c_rank INT;
BEGIN
    OPEN c_user;
    LOOP
    FETCH c_user
    INTO c_id, c_rank;
EXIT WHEN NOT FOUND;
IF (c_rank >= holidayGift.p_rank) THEN
UPDATE users SET money = money + p_money WHERE summonername = c_id;
SELECT cname
INTO STRICT
unownedChampion FROM champions
WHERE cname NOT IN
(
SELECT champion
FROM ownedChampions
WHERE summonername = c_id)
AND price >= ALL
(
SELECT price
FROM champions
WHERE cname NOT IN (
SELECT champion
FROM ownedchampions
WHERE summonername = c_id));
IF NOT FOUND THEN
RAISE EXCEPTION 'Users % has all champions', p_summonername;
END
IF;
INSERT INTO ownedChampions
values(c_id, unownedChampion);
END
IF;
END LOOP;
CLOSE c_user;
END;
$$
LANGUAGE 'plpgsql' VOLATILE
SECURITY DEFINER;

--Trigger
DROP TRIGGER IF EXISTS tr_increase_champion_price
ON ownedChampions;
DROP FUNCTION IF EXISTS increase_champion_price
();

CREATE OR REPLACE FUNCTION increase_champion_price
()
RETURNS TRIGGER AS
$BODY$
BEGIN
    UPDATE champions SET price=price+1 WHERE cname=NEW.champion;
    RETURN NEW;
END;
$BODY$
LANGUAGE 'plpgsql' VOLATILE
SECURITY DEFINER;

CREATE TRIGGER tr_increase_champion_price AFTER
INSERT ON
ownedChampions
FOR
EACH
ROW
EXECUTE PROCEDURE increase_champion_price
();