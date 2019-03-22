import psycopg2
import datetime
import hashlib
import random
import re

from getpass import getpass
from validate_email import validate_email


def connect(prompt):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')

        # Please edit this to match your database name and its connection settings
        conn = psycopg2.connect(user="postgres",
                                password="postgres",
                                host="localhost",
                                port="5432",
                                database="postgres")

        # create a cursor
        cur = conn.cursor()

 # execute a statement
        if prompt == 1:
            print('\nAdd a new user\n')
            addUser(conn, cur)
        elif prompt == 2:
            print('\nCreate a squad\n')
            createSquad(conn, cur)
        elif prompt == 3:
            print('\nSimulate a game\n')
            addGame(conn, cur)
        elif prompt == 4:
            print('\nBuy a champion or a skin\n')
            buyChampionOrSkin(conn, cur)
        elif prompt == 5:
            print('\nSimulate a new tournament\n')
            competeInTournament(conn, cur)
         # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.Error) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def addUser(conn, cur):
    summonername = input("Enter summoner name: ")
    isValidSummonerName = re.match("^[A-Za-z0-9]*$", summonername)

    while not isValidSummonerName:
        print("Error: Invalid summoner name entered. Please ensure that it only contains letters and digits.")
        summonername = input("Enter summoner name: ")
        isValidSummonerName = re.match("^[A-Za-z0-9]*$", summonername)

    cur.execute(
        "SELECT summonername FROM users WHERE summonername=%s", [summonername])
    if cur.fetchone() != None:
        print("Error: The summoner name provided already exists.")
        return

    email = input("\nEnter email: ")
    isValidEmail = validate_email(email)

    while not isValidEmail:
        print("Error: Invalid email entered.")
        email = input("Enter email: ")
        isValidEmail = validate_email(email)

    password = getpass("\nEnter password: ")
    status = "offline"
    level = 0
    rank = 0
    money = random.randint(400, 1000)

    hashedPassword = hashlib.md5(password.encode()).hexdigest()

    cur.execute(
        'INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)', [summonername, email, hashedPassword, status, level, rank, money])

    conn.commit()
    print("\nUser %s created successfully." % (summonername))

    print("\nNew entries in the users table: \n(summonername, email, password, status, level, rank, money, squad)")
    cur.execute(
        "SELECT * FROM users WHERE summonername=%s", [summonername])
    result = cur.fetchall()
    for i in result:
        print(i)


def createSquad(conn, cur):
    input_string = input(
        "Enter five summoner names forming the squad separated with spaces: ")
    list = input_string.split()

    while len(list) != 5 or len(list) != len(set(list)):
        print("Error: There must be exactly five distinct users in the squad.")
        input_string = input(
            "Enter five summoner names forming the squad separated with spaces: ")
        list = input_string.split()

    for i in list:
        cur.execute(
            "SELECT * FROM users WHERE summonername=%s", [i])
        row = cur.fetchone()
        if row == None:
            print("Error: User %s does not exist." % (i))
            return

        cur.execute(
            "SELECT squad FROM users WHERE summonername=%s AND squad IS NOT NULL", [i])
        row2 = cur.fetchone()
        if row2 != None:
            print("Error: User %s is already in a squad." % (i))
            return

    sqName = input("\nName your squad: ")
    isValidSquadName = re.match("^[A-Za-z0-9 ]*$", sqName)

    while not isValidSquadName:
        print("Error: Invalid squad name. Please ensure that it only contains letters, numbers and spaces.")
        sqName = input("Name your squad: ")
        isValidSquadName = re.match("^[A-Za-z0-9 ]*$", sqName)

    cur.execute("SELECT sqname FROM squads WHERE sqname=%s", [sqName])
    if cur.fetchone() != None:
        print("Error: The squad name provided already exists.")
        return

    # Set rank to one more than the lowest ranked squad
    cur.execute("SELECT max(sqrank) FROM squads")
    lowestRank = [record for record in cur.fetchone()]
    rank = int(lowestRank[0]) + 1

    cur.execute("INSERT INTO squads VALUES (%s, %s)", [sqName, rank])
    conn.commit()

    for i in list:
        cur.execute(
            "UPDATE users SET squad=%s WHERE summonername=%s", [sqName, i])
        conn.commit()

    print("\nSquad %s created successfully." % (sqName))

    print("\nNew entries in the squads table:\n(sqname, sqrank)")
    cur.execute(
        "SELECT * FROM squads WHERE sqname=%s", [sqName])
    result = cur.fetchall()
    for i in result:
        print(i)

    print("\nUpdated entries in the users table: \n(summonername, squad)")
    cur.execute(
        "SELECT summonername, squad FROM users WHERE squad=%s", [sqName])
    result = cur.fetchall()
    for i in result:
        print(i)


def addGame(conn, cur):
    print("Maps available:")
    cur.execute("SELECT * FROM maps")
    result = cur.fetchall()
    for i in result:
        print(i)
    mapSel = int(input(
        "\nPlease enter the ID of the map you wish to select or enter 0 to create a new one: "))
    if mapSel == 0:
        themeInt = int(input(
            "\nPlease enter the number corresponding to the theme:\n0: Summoner's rift\n1: Twisted treeline\n2: Howling abyss\nInput: "))
        while themeInt < 0 or themeInt > 2:
            print("Error: Invalid input. Please only enter 0, 1 or 2.")
            themeInt = int(input(
                "\nPlease enter the number corresponding to the theme:\n0: Summoner's rift\n1: Twisted treeline\n2: Howling abyss\nInput: "))

        if themeInt == 0:
            theme = 'Summoner\'s rift'
        elif themeInt == 1:
            theme = 'Twisted treeline'
        elif themeInt == 2:
            theme = 'Howling abyss'

        numTurrets = random.randint(10, 100)

        # Set mapid to one more than the highest mapid
        cur.execute("SELECT max(mapid) FROM maps")
        highestMapid = [record for record in cur.fetchone()]
        mapid = int(highestMapid[0]) + 1

        cur.execute("INSERT INTO maps VALUES (%s, %s, %s)",
                    [mapid, theme, numTurrets])
        conn.commit()

        print("\nSuccessfully added map with ID %d." % mapid)

        print("\nNew entries in maps table:\n(mapid, theme, turretscount)")
        cur.execute("SELECT * FROM maps where mapid=%s", [mapid])
        result = cur.fetchall()
        for i in result:
            print(i)
    else:
        cur.execute("SELECT mapid FROM maps where mapid=%s", [mapSel])
        result = cur.fetchone()
        if result != None:
            maprec = [record for record in result]
            mapid = int(maprec[0])
            print("\nMap selected: %d." % (mapid))
        else:
            print("Error: No map exists with ID %d" % (mapSel))
            return

    cur.execute("SELECT * FROM gamemodes where map=%s", [mapid])
    result = cur.fetchall()
    if result != []:
        print("\nGame modes with mapid %d:\n(id, type, formation, reward, punishment, map)" % (mapid))
        for i in result:
            print(i)
        gmSel = int(input(
            "\nPlease enter the ID of the game mode you wish to select or enter 0 to create a new one: "))
        if gmSel == 0:
            gmid = createGameMode(mapid, conn, cur)
        else:
            cur.execute(
                "SELECT id FROM gameModes where id=%s AND map=%s", [gmSel, mapid])
            result = cur.fetchone()
            if result != None:
                gmrec = [record for record in result]
                gmid = int(gmrec[0])
            else:
                print("Error: No game modes exists with ID %d and map ID %d" %
                      (gmSel, mapid))
                return
    else:
        print("\nNo game modes available with mapid %d. Creating a new one." % (mapid))
        gmid = createGameMode(mapid, conn, cur)

    print("\nGame mode #%d selected." % gmid)
    cur.execute(
        "SELECT * FROM gameModes where id=%s", [gmid])
    result = cur.fetchone()
    (gmid, gtype, formation, reward, punishment, mapid) = result

    # Set gameid to one more than the highest gameid
    cur.execute("SELECT max(gameid) FROM gameInstances")
    highestGameid = [record for record in cur.fetchone()]
    gameid = int(highestGameid[0]) + 1

    # Set patch equal to the highest patch
    cur.execute("SELECT max(patch) FROM gameInstances")
    highestPatch = [record for record in cur.fetchone()]
    patch = int(highestPatch[0])

    tstamp = ("%s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    # Co-op vs ai mode: only need one team of players, the other team is AI
    if gtype == 'co-op vs ai':
        if formation == "5v5":
            numPlayers = 5
        elif formation == "3v3":
            numPlayers = 3
        elif formation == "1v1":
            numPlayers = 1
    # All othergame modes: two teams of players
    else:
        if formation == "5v5":
            numPlayers = 10
        elif formation == "3v3":
            numPlayers = 6
        elif formation == "1v1":
            numPlayers = 2

    input_string = input(
        "\nEnter " + str(numPlayers) + " summoner names for this game: ")
    list1 = input_string.split()

    while len(list1) != numPlayers or len(list1) != len(set(list1)):
        print("Error: There must be exactly",
              numPlayers, "distinct players in this game.")
        input_string = input(
            "Enter " + str(numPlayers) + " summoner names for this game: ")
        list1 = input_string.split()

    # Check users' existence
    for i in list1:
        cur.execute(
            "SELECT * FROM users WHERE summonername=%s", [i])
        row = cur.fetchone()
        if row == None:
            print("Error: User %s does not exist." % (i))
            return

    redCt = numPlayers/2
    blueCt = numPlayers/2

    playerRows = []

    for player in list1:
        # Choose a champion
        cur.execute(
            "SELECT cname, hp, ad, asp, msp, mana, hr, armor, magicresist FROM champions WHERE cname IN (SELECT champion FROM ownedChampions WHERE summonerName=%s) ORDER BY cname", [player])
        result = cur.fetchall()
        if result == []:
            print("Error: %s does not own any champions." % (player))
            return
        print("Here are the champions %s may choose:\n(cname, hp, ad, asp, msp, mana, hr, armor, magicresist)" % (player))
        for j in result:
            print(j)
        cname = input(
            "\nPlease choose the desired champion for " + player + ": ")
        cur.execute("SELECT * FROM champions WHERE cname=%s AND cname IN (SELECT champion FROM ownedChampions WHERE summonerName=%s)",
                    [cname, player])
        r = cur.fetchone()
        if r == None:
            print("Error: Invalid champion name or you do not yet own it.")
            return

        # Choose a skin
        cur.execute(
            "SELECT skname, rp, rarity FROM skins WHERE skname IN (SELECT skname FROM ownedskins WHERE summonername=%s) AND champion=%s ORDER BY skname", [player, cname])
        result = cur.fetchall()
        if result == []:
            print(
                "You do not own any skins for champion %s. Using default skin." % (cname))
            skname = "0"
        else:
            print(
                "\nHere are the skins available for your champion %s:\n(skname, rp, rarity)" % (cname))
            for j in result:
                print(j)
            skname = input("Please choose the desired skin for " +
                           cname + " or enter 0 for default skin: ")
            if skname != "0":
                cur.execute(
                    "SELECT * FROM skins WHERE skname=%s AND skname IN (SELECT skname FROM ownedskins WHERE summonername=%s) AND champion=%s ORDER BY skname", [skname, player, cname])
                r = cur.fetchone()
                if r == None:
                    print(
                        "Error: Invalid skin name or you do not yet own it. Using default skin.")
                    skname = "default"

        # Choose game items(optional)
        print("\nHere are the in game items available:\n(giName, type, cost, ad, asp, crit, mana, ap, cdr, hp, armor, mr)")
        cur.execute("SELECT * FROM inGameItems")
        result = cur.fetchall()
        for j in result:
            print(j)
        listOfItems = []
        while 1:
            giname = input(
                "Please enter the name of one item you want to carry or enter 0 when you are done: ")
            if giname != "0":
                cur.execute(
                    "SELECT * FROM inGameItems WHERE giname=%s", [giname])
                r = cur.fetchone()
                if (r != None):
                    print("Successfully added item %s" % (giname))
                    listOfItems.append(giname)
                else:
                    print("Invalid item. Please try again.")
            else:
                break

        # Pick team at random if not co-op vs ai type
        if gtype != 'co-op vs ai':
            rand = random.randint(0, 2)

            if redCt > 0 and blueCt > 0:
                if rand == 0:
                    team = "red"
                    redCt -= 1
                else:
                    team = "blue"
                    blueCt -= 1
            elif redCt == 0 and blueCt > 0:
                team = "blue"
                blueCt -= 1
            elif blueCt == 0 and redCt > 0:
                team = "red"
                redCt -= 1
        # Otherwise, players form the red team and AIs form the blue team
        else:
            team = "red"

        if skname == "0":
            skname = "default"
        print("\n%s has been assigned team %s with champion %s, skin %s and items %s" % (
            player, team, cname, skname, str(listOfItems)))

        playerRows.append([player, gameid, team, random.randint(1, 250), random.randint(8000, 30000), random.randint(
            0, 8), random.randint(0, 15), random.randint(0, 15), cname, skname, listOfItems])

    teams = ['red', 'blue']
    winner = random.choice(teams)

    # Add game instance to gameinstances table
    cur.execute("INSERT INTO gameinstances VALUES (%s, %s, %s, %s, %s)", [
                gameid, patch, tstamp, winner, gmid])
    conn.commit()
    print("\nSuccessfully added game instance %s in gameinstances table." % (gameid))
    print(
        "\nNew entries in the gameinstances table:\n(gameid, patch, tstamp, winner, gmode)")
    cur.execute("SELECT * FROM gameinstances WHERE gameid=%s", [gameid])
    result = cur.fetchall()
    for j in result:
        print(j)

    print()

    for row in playerRows:
        listOfItems = row[10]
        if row[9] != "default":
            cur.execute(
                "INSERT INTO players VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]])
        else:
            cur.execute(
                "INSERT INTO players VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)", [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]])

        conn.commit()
        print("Successfully added player %s in players table." % (row[0]))

        if len(listOfItems) != 0:
            for item in listOfItems:
                cur.execute("INSERT INTO carries VALUES (%s, %s, %s, %s)", [
                            row[0], row[8], row[1], item])
                conn.commit()
                print(
                    "Successfully added game item %s for player %s in carries table." % (item, row[0]))

    print("\nNew entries in players table:\n(playername, gameid, team, cs, gold, death, kill, assist, champion, skin)")
    cur.execute(
        "SELECT * FROM players WHERE gameid=%s", [gameid])
    result = cur.fetchall()
    for j in result:
        print(j)

    print("\nNew entries in carries table:\n(player, champion, gameid, item)")
    cur.execute(
        "SELECT * FROM carries WHERE gameid=%s", [gameid])
    result = cur.fetchall()
    for j in result:
        print(j)

    print()

    # Add entries in playedin with outcome
    for i in list1:
        cur.execute(
            "SELECT team FROM players WHERE playerName=%s AND gameid=%s", [i, gameid])
        result = cur.fetchone()
        rec = [record for record in result]
        t = rec[0]

        if t == winner:
            outcome = 'win'
        else:
            outcome = 'loss'

        cur.execute("INSERT INTO playedin VALUES (%s, %s, %s)",
                    [i, gameid, outcome])
        conn.commit()
        print("Succesfully recorded a %s for player %s in game #%s" %
              (outcome, i, gameid))

    if gtype == 'ranked':
        # Level up all winners
        cur.execute(
            "UPDATE users SET level=level+1 WHERE summonername IN (SELECT summonername FROM playedin WHERE gameid=%s AND outcome='win')", [gameid])
        conn.commit()
        print("\nSuccessfully updated level for winners of game #%d" % (gameid))

    # Update the money for users in the game
    # Add reward to winners
    cur.execute(
        "UPDATE users SET money=money+(SELECT reward FROM gamemodes WHERE id=(SELECT gmode FROM gameinstances WHERE gameid=%s)) WHERE summonername IN (SELECT summonername FROM playedin WHERE gameid=%s AND outcome='win')", [gameid, gameid])
    conn.commit()
    # Subtract punishment to losers
    cur.execute(
        "UPDATE users SET money=money+(SELECT punishment FROM gamemodes WHERE id=(SELECT gmode FROM gameinstances WHERE gameid=%s)) WHERE summonername IN (SELECT summonername FROM playedin WHERE gameid=%s AND outcome='loss')", [gameid, gameid])
    conn.commit()
    print("\nSuccessfully updated money for users in game #%d" % (gameid))

    # Display only level if game type is ranked
    if gtype == 'ranked':
        print("\nUpdated entries in users table:\n(summonername, level, money)")
        cur.execute(
            "SELECT summonername, level, money FROM users WHERE summonername IN (SELECT summonername FROM playedin WHERE gameid=%s)", [gameid])
    else:
        print("\nUpdated entries in users table:\n(summonername, money)")
        cur.execute(
            "SELECT summonername, money FROM users WHERE summonername IN (SELECT summonername FROM playedin WHERE gameid=%s)", [gameid])
    result = cur.fetchall()
    for j in result:
        print(j)


def createGameMode(mapid, conn, cur):
    gtypeInt = int(input(
        "\nPlease enter the number corresponding to the game type:\n0: casual\n1: ranked\n2: co-op vs ai\n3: custom\nInput: "))
    while gtypeInt < 0 or gtypeInt > 3:
        print("Error: Invalid input. Please only enter 0, 1, 2 or 3.")
        gtypeInt = int(input(
            "Please enter the number corresponding to the game type:\n0: casual\n1: ranked\n2: co-op vs ai\n3: custom\nInput: "))
    formationInt = int(input(
        "\nPlease enter the number corresponding to the formation:\n1: 1v1\n3: 3v3\n5: 5v5\nInput: "))
    while formationInt != 1 and formationInt != 3 and formationInt != 5:
        print("Error: Invalid input. Please only enter 1, 3 or 5.")
        formationInt = int(input(
            "Please enter the number corresponding to the formation:\n1: 1v1\n3: 3v3\n5: 5v5\nInput: "))

    if gtypeInt == 0:
        gtype = "casual"
    elif gtypeInt == 1:
        gtype = "ranked"
    elif gtype == 2:
        gtype = "co-op vs ai"
    elif gtype == 3:
        gtype = "custom"

    if formationInt == 5:
        formation = "5v5"
    elif formationInt == 3:
        formation = "3v3"
    elif formationInt == 1:
        formation = "1v1"

    reward = random.randint(100, 900)
    punishment = -1 * random.randint(25, int(reward/2))

    # Set id to one more than the highest id
    cur.execute("SELECT max(id) FROM gamemodes")
    highestGmid = [record for record in cur.fetchone()]
    gmid = int(highestGmid[0]) + 1

    cur.execute("INSERT INTO gamemodes VALUES (%s, %s, %s, %s, %s, %s)",
                [gmid, gtype, formation, reward, punishment, mapid])
    conn.commit()

    print("\nSuccessfully added game mode with ID %d" % gmid)

    print("\nNew entries in gamemodes table:")
    cur.execute("SELECT * FROM gamemodes where id=%s", [gmid])
    result = cur.fetchall()
    for i in result:
        print(i)

    return gmid


def buyChampionOrSkin(conn, cur):
    summonername = input("Enter summoner name: ")
    isValidSummonerName = re.match("^[A-Za-z0-9]*$", summonername)

    while not isValidSummonerName:
        print("Error: Invalid summoner name entered. Please ensure that it only contains letters and digits.")
        summonername = input("Enter summoner name: ")
        isValidSummonerName = re.match("^[A-Za-z0-9]*$", summonername)

    cur.execute(
        "SELECT * FROM users WHERE summonername=%s", [summonername])
    row = cur.fetchone()
    if row == None:
        print("Error: User %s does not exist." % (summonername))
        return
    money = float(row[6])

    itemType = int(
        input("\nEnter the type of item you want to buy:\n1: champion\n2: skin\nInput: "))

    while itemType < 1 or itemType > 2:
        print("Error: Invalid item type. Please enter 1 or 2 only.")
        itemType = int(
            input("Enter the type of item you want to buy:\n1: champion\n2: skin\nInput: "))

    print("You currently have %f money." % (money))
    if itemType == 1:
        cur.execute(
            "SELECT * FROM champions WHERE price<=%s AND cname NOT IN (SELECT champion FROM ownedChampions WHERE summonerName=%s) ORDER BY cname", [money, summonername])
        result = cur.fetchall()
        if result != []:
            print(
                "Here are the champions you can buy and that you do not own:\n(cname, price, hp, ad, asp, msp, mana, hr, armor, magicresist)")
            for i in result:
                print(i)
            cname = input(
                "Please enter the name of the champion you wish to buy: ")

            cur.execute("SELECT * FROM champions WHERE cname=%s AND price<=%s AND cname NOT IN (SELECT champion FROM ownedChampions WHERE summonerName=%s)",
                        [cname, money, summonername])
            r = cur.fetchone()
            if r == None:
                print(
                    "Error: Purchase failed. Invalid champion name or you cannot buy it.")
                return
            else:
                cur.execute("INSERT INTO ownedChampions VALUES (%s, %s)", [
                            summonername, cname])
                conn.commit()
                cur.execute(
                    "UPDATE users SET money=money-(SELECT price FROM champions WHERE cname=%s) WHERE summonername=%s", [cname, summonername])
                conn.commit()
                cur.execute(
                    "SELECT money FROM users WHERE summonername=%s", [summonername])
                row = cur.fetchone()
                newMoney = float(row[0])
                print("\nSuccessfully purchased champion %s.\nYou now have %f money." % (
                    cname, newMoney))

                print("\nNew entries in ownedChampions table:\n(summonername, champion)")
                cur.execute(
                    "SELECT * FROM ownedChampions WHERE summonername=%s AND champion=%s", [summonername, cname])
                result = cur.fetchall()
                for i in result:
                    print(i)

                print(
                    "\nUpdated entries in users table:\n(summonername, money)")
                cur.execute(
                    "\nSELECT summonername, money FROM users WHERE summonername=%s", [summonername])
                result = cur.fetchall()
                for i in result:
                    print(i)
        else:
            print("Error: There are no champions that you can buy.")
            return
    elif itemType == 2:
        cur.execute(
            "SELECT * FROM skins WHERE price<=%s AND champion IN (SELECT champion FROM ownedChampions WHERE summonerName=%s) AND skname NOT IN (SELECT skin FROM ownedSkins WHERE summonername=%s) ORDER BY skname", [money, summonername, summonername])
        result = cur.fetchall()
        if result != []:
            print(
                "Here are the skins you can buy for your champions and that you do not own:\n(skname, price, rp, rarity, champion)")
            for i in result:
                print(i)
            skname = input(
                "Please enter the name of the skin you wish to buy: ")

            cur.execute("SELECT * FROM skins WHERE skname=%s AND price<=%s AND skname NOT IN (SELECT skin FROM ownedSkins WHERE summonername=%s) AND champion IN (SELECT champion FROM ownedChampions WHERE summonerName=%s)",
                        [skname, money, summonername, summonername])
            r = cur.fetchone()
            if r == None:
                print(
                    "Error: Purchase failed. Invalid skin name or you cannot buy it.")
                return
            else:
                cur.execute("INSERT INTO ownedSkins VALUES (%s, %s)", [
                            summonername, skname])
                conn.commit()
                cur.execute(
                    "UPDATE users SET money=money-(SELECT price FROM skins WHERE skname=%s) WHERE summonername=%s", [skname, summonername])
                conn.commit()
                cur.execute(
                    "SELECT money FROM users WHERE summonername=%s", [summonername])
                row = cur.fetchone()
                newMoney = float(row[0])
                print("\nSuccessfully purchased skin %s.\nYou now have %f money." % (
                    skname, newMoney))

                print("\nNew entries in ownedSkins table:\n(summonername, skin)")
                cur.execute(
                    "SELECT * FROM ownedSkins WHERE summonername=%s AND skin=%s", [summonername, skname])
                result = cur.fetchall()
                for i in result:
                    print(i)

                print(
                    "\nUpdated entries in users table:\n(summonername, money)")
                cur.execute(
                    "SELECT summonername, money FROM users WHERE summonername=%s", [summonername])
                result = cur.fetchall()
                for i in result:
                    print(i)
        else:
            print("Error: There are no skins that you can buy.")
            return


def competeInTournament(conn, cur):
    input_string = input(
        "Enter squad names that will compete in this tournament, separated by a semicolon (example: squad 1;squad 2;squad 3;etc.): ")
    squads = input_string.split(";")

    while len(squads) != len(set(squads)) or len(set(squads)) < 3:
        print("Error: All squads must be distinct and there must be a minimum of three squads in a tournament.")
        input_string = input(
            "Enter squad names that will compete in this tournament, separated by a semicolon (example: squad 1;squad 2;squad 3;etc.): ")
        squads = input_string.split(";")

    # Check squads' existence
    for i in squads:
        cur.execute(
            "SELECT * FROM squads WHERE sqname=%s", [i])
        row = cur.fetchone()
        if row == None:
            print("Error: Squad %s does not exist." % (i))
            return

    now = ("%s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    ttype = input("\nPossible tournament types: casual, invitational, all-star, local, national, regional, world\nEnter the type of tounament you wish to create: ").lower()
    types = ['casual', 'invitational', 'all-star', 'local', 'national', 'regional', 'world']
    while ttype not in types:
        print("Error: Invalid tournament type.")
        ttype = input("Possible tournament types: casual, invitational, all-star, local, national, regional, world\nEnter the type of tounament you wish to create: ").lower()

    if ttype == 'casual':
        prizemax = random.randint(1, 21)
    elif ttype == 'national' or ttype == 'local' or ttype == 'invitational':
        prizemax = random.randint(5, 101)
    elif ttype == 'regional' or ttype == 'all-star':
        prizemax = random.randint(50, 501)
    elif ttype == 'world':
        prizemax = random.randint(100, 1001)
    prizes = 1000 * prizemax

    location = input("\nPlease enter the location where the tournament is held: ")

    # Set tourid to one more than the highest gameid
    cur.execute("SELECT max(tourid) FROM tournaments")
    highestTourid = [record for record in cur.fetchone()]
    tourid = int(highestTourid[0]) + 1

    # Shuffle the ranks
    numsquads = len(squads)
    ranks = [i for i in range(1, numsquads + 1)]
    random.shuffle(ranks)

    competesInRows = []
    
    index = 0
    for i in squads:
        # Assign random ranks to squads
        competesInRows.append([i, ranks[index]])
        index += 1

    for row in competesInRows:
        if row[1] == 1:
            winner = row[0]

    cur.execute("INSERT INTO tournaments VALUES (%s, %s, %s, %s, %s, %s)", [tourid, prizes, winner, ttype, now, location])
    conn.commit()
    print("\nSuccessfully added tournament #%d in tournaments table." % (tourid))
    print("\nNew entries in tournaments table:\n(tourid, prizes, winningsquad, type, tstamp, location)")
    cur.execute("SELECT * FROM tournaments WHERE tourid=%s", [tourid])
    result = cur.fetchall()
    for i in result:
        print(i)
    
    for row in competesInRows:
        cur.execute("INSERT INTO competesin VALUES (%s, %s, %s)", [row[0], tourid, row[1]])
        conn.commit()
    print("\nSuccessfully added squads for tournaments #%d in competesin table." % (tourid))
    print("\nNew entries in competesin table:\n(squad, tourid, tplace)")
    cur.execute("SELECT * FROM competesin WHERE tourid=%s", [tourid])
    result = cur.fetchall()
    for i in result:
        print(i)

    cur.execute("UPDATE users SET money=money+%s WHERE squad=%s", [prizes, winner])
    conn.commit()
    print("\nSuccessfully updated money for winners of tournament #%d in users table." % (tourid))
    print("\nUpdated entries in users table:\n(summonername, squad, money)")
    cur.execute("SELECT summonername, squad, money FROM users WHERE squad=%s", [winner])
    result = cur.fetchall()
    for i in result:
        print(i)

    return


if __name__ == '__main__':
    while 1:
        print("""Options:
1: Add a new user
2: Create a new squad
3: Simulate a game
4: Buy a champion or a skin
5: Simulate a new tournament
Any other input: exit
""")
        prompt = int(input("Enter a command: "))
        if prompt >= 1 and prompt <= 5:
            connect(prompt)
            print()
        else:
            exit(1)
