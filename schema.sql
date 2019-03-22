DROP TABLE IF EXISTS users;
CREATE TABLE users
(
    summonerName varchar(16) PRIMARY KEY NOT NULL,
    email varchar(255) NOT NULL,
    password varchar(32) NOT NULL,
    status varchar(64),
    level integer NOT NULL CHECK(level >= 0),
    rank integer NOT NULL CHECK(rank >= 0 AND rank <= 8),
    money double precision NOT NULL CHECK(money >= 0.0),
    squad varchar(16),
    FOREIGN KEY (squad) REFERENCES squads(sqname)
);

DROP TABLE IF EXISTS maps;
CREATE TABLE maps
(
    mapID integer PRIMARY KEY NOT NULL,
    theme varchar(32) NOT NULL,
    turrentCount integer NOT NULL CHECK (turrentCount >= 10)
);

DROP TABLE IF EXISTS gameModes;
CREATE TABLE gameModes
(
    id varchar(8) PRIMARY KEY NOT NULL,
    type varchar(12) NOT NULL,
    formation varchar(3) NOT NULL,
    reward double precision,
    punishment double precision,
    map integer NOT NULL,
    FOREIGN KEY (map) REFERENCES maps(mapID)
);

DROP TABLE IF EXISTS gameInstances;
CREATE TABLE gameInstances
(
    gameID bigint PRIMARY KEY NOT NULL,
    patch integer NOT NULL CHECK(patch > 0),
    tstamp timestamp NOT NULL,
    winner varchar(4),
    gMode integer NOT NULL,
    FOREIGN KEY (gMode) REFERENCES gameModes(id)
);

DROP TABLE IF EXISTS champions;
CREATE TABLE champions
(
    cName varchar(16) PRIMARY KEY NOT NULL,
    price double precision NOT NULL CHECK (price >= 0.0),
    hp double precision CHECK (hp >= 0.0),
    ad double precision CHECK (ad >= 0.0),
    asp double precision CHECK (asp >= 0.0),
    msp double precision CHECK (msp >= 0.0),
    mana double precision CHECK (mana >= 0.0),
    hr double precision CHECK (hr >= 0.0),
    armor double precision CHECK (armor >= 0.0),
    magicResist double precision CHECK (magicResist >= 0.0)
);

DROP TABLE IF EXISTS skins;
CREATE TABLE skins
(
    skName varchar(255) PRIMARY KEY NOT NULL,
    price double precision NOT NULL CHECK (price >= 0.0),
    rp integer CHECK (rp >= 0),
    rarity integer CHECK (rarity >= 0),
    champion varchar(16),
    FOREIGN KEY (champion) REFERENCES champions(cName)
);

DROP TABLE IF EXISTS inGameItems;
CREATE TABLE inGameItems
(
    giName varchar(128) PRIMARY KEY NOT NULL,
    type varchar(9) NOT NULL CHECK (type='Offensive' OR type='Magical' OR type='Defensive'),
    cost integer NOT NULL CHECK (cost >= 0),
    ad integer,
    asp double precision,
    crit double precision,
    mana integer,
    ap integer,
    cdr double precision,
    hp integer,
    armor integer,
    mr integer
);

DROP TABLE IF EXISTS squads;
CREATE TABLE squads
(
    sqName varchar(16) PRIMARY KEY NOT NULL,
    sqRank integer NOT NULL CHECK (sqRank > 0)
);

DROP TABLE IF EXISTS tournaments;
CREATE TABLE tournaments
(
    tourID integer PRIMARY KEY NOT NULL,
    prizes double precision NOT NULL,
    winningSquad varchar(16),
    type varchar(64) NOT NULL,
    tstamp timestamp NOT NULL,
    location varchar(255) NOT NULL,
    FOREIGN KEY (winningSquad) REFERENCES squads(sqName)
);

DROP TABLE IF EXISTS players;
CREATE TABLE players
(
    playerName varchar(16) NOT NULL,
    gameID integer NOT NULL,
    team varchar(4) NOT NULL CHECK (team='red' OR team='blue'),
    cs integer CHECK (cs >= 0),
    gold integer NOT NULL CHECK (gold >= 0),
    death integer NOT NULL CHECK (death >= 0),
    kill integer NOT NULL CHECK
    (
    kill >= 0),
assist integer NOT NULL CHECK
    (assist >= 0),
champion varchar
    (16) NOT NULL,
skin varchar
    (255),
UNIQUE
    (playerName, gameID),
PRIMARY KEY
    (playerName, gameID),
FOREIGN KEY
    (playerName) REFERENCES users
    (summonerName),
FOREIGN KEY
    (gameID) REFERENCES gameInstances
    (gameID),
FOREIGN KEY
    (champion) REFERENCES champions
    (cName),
FOREIGN KEY
    (skin) REFERENCES skin
    (skName)
);

    DROP TABLE IF EXISTS friends;
    CREATE TABLE friends
    (
        summonerName varchar(16) NOT NULL,
        friendName varchar(16) NOT NULL,
        PRIMARY KEY (summonerName, friendName),
        FOREIGN KEY (summonerName) REFERENCES users(summonerName),
        FOREIGN KEY (friendName) REFERENCES users(summonerName)
    );

    DROP TABLE IF EXISTS playedIn;
    CREATE TABLE playedIn
    (
        summonerName varchar(16) NOT NULL,
        gameID integer NOT NULL,
        outcome varchar(4) CHECK (outcome='win' OR outcome='loss'),
        UNIQUE (summonerName, gameID),
        PRIMARY KEY (summonerName, gameID),
        FOREIGN KEY (summonerName) REFERENCES users(summonerName),
        FOREIGN KEY (gameID) REFERENCES gameInstances(gameID)
    );

    DROP TABLE IF EXISTS carries;
    CREATE TABLE carries
    (
        player varchar(16) NOT NULL,
        champion varchar(16) NOT NULL,
        gameID integer NOT NULL,
        item varchar(128) NOT NULL,
        PRIMARY KEY (player, gameID, item),
        FOREIGN KEY (player) REFERENCES users(summonerName),
        FOREIGN KEY (champion) REFERENCES champions(cName),
        FOREIGN KEY (gameID) REFERENCES gameInstances(gameID),
        FOREIGN KEY (item) REFERENCES inGameItems(giName)
    );

    DROP TABLE IF EXISTS ownedChampions;
    CREATE TABLE ownedChampions
    (
        summonerName varchar(16) NOT NULL,
        champion varchar(255) NOT NULL,
        PRIMARY KEY (summonerName, champion),
        FOREIGN KEY (summonerName) REFERENCES users(summonerName),
        FOREIGN KEY (champion) REFERENCES champions(cName)
    );

    DROP TABLE IF EXISTS ownedSkins;
    CREATE TABLE ownedSkins
    (
        summonerName varchar(16) NOT NULL,
        skin varchar(255) NOT NULL,
        PRIMARY KEY (summonerName, skin),
        FOREIGN KEY (summonerName) REFERENCES users(summonerName),
        FOREIGN KEY (skin) REFERENCES skins(skName)
    );

    DROP TABLE IF EXISTS competesIn;
    CREATE TABLE competesIn
    (
        squad varchar(16) PRIMARY KEY NOT NULL,
        tourID integer NOT NULL,
        tplace integer NOT NULL,
        PRIMARY KEY (squad, tourID),
        FOREIGN KEY (squad) REFERENCES squads(sqName),
        FOREIGN KEY (tourID) REFERENCES tournaments(tourID)
    ); 
