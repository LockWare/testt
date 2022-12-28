import os
from dotenv import load_dotenv, find_dotenv
import mysql.connector
import requests
import random
import string
import time
load_dotenv(find_dotenv())

def OpenDBConnection():
    MYSQLDB = mysql.connector.connect(
        host=os.getenv('MYSQLDATABASE'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        database=os.getenv('MYSQL_SCHEMA'),
        port=int(os.getenv('DBPORT'))
    )
    return MYSQLDB, MYSQLDB.cursor()

def findtokenbyhash(hash):
    MYSQLDB, cursor = OpenDBConnection()
    cursor.execute("SELECT * FROM admintokens WHERE tokenhash = (%s)", (hash,))
    result = cursor.fetchone()
    cursor.close()
    if result is None:
        return None
    return {
        "id":result[0],
        "tokenhash":result[1],
        "created":result[2],
        "creatorhash":result[3],
        "adminlevel":result[4]
    }

def setblackliststatus(placeid, status):
    MYSQLDB, cursor = OpenDBConnection()
    cursor.execute("UPDATE places SET isblacklisted = (%s) WHERE placeid = (%s)", (status, placeid))
    MYSQLDB.commit()
    cursor.close()

def get_server_count(placeid):
    MYSQLDB, cursor = OpenDBConnection()
    MYSQLDB.commit()
    cursor.execute(f"SELECT COUNT(*) FROM vipservers WHERE placeid = (%s) AND isvalid = 1", (str(placeid),))
    result = cursor.fetchone()[0]
    cursor.close()
    return result

def get_server_info(serverid):
    # gets info from vipservers table returns first match
    MYSQLDB, cursor = OpenDBConnection()
    MYSQLDB.commit()
    cursor.execute(f"SELECT * FROM vipservers WHERE serverid = (%s)", (str(serverid),))
    results = cursor.fetchone()
    cursor.close()
    if results is None:
        return None
    return {"serverid":serverid,"placeid":results[1],"serverlinkcode":results[2],"uploaded":results[3],"lastchecked":results[4],"uploaderhash":results[5],"isvalid":bool(results[6])}

def get_server_list(placeid):
    # gets list of servers from vipservers table which matches placeid and sort by last updated in descending order
    MYSQLDB, cursor = OpenDBConnection()
    MYSQLDB.commit()
    cursor.execute(f"SELECT * FROM vipservers WHERE placeid = (%s) AND isvalid = 1 ORDER BY lastchecked DESC", (str(placeid),))
    result = cursor.fetchall()
    cursor.close()
    return result

def getallservers(placeid):
    MYSQLDB, cursor = OpenDBConnection()
    MYSQLDB.commit()
    cursor.execute(f"SELECT * FROM vipservers WHERE placeid = (%s)", (str(placeid),))
    result = cursor.fetchall()
    cursor.close()
    return result

def get_game_info(placeid):
    # gets info from places table returns first match
    MYSQLDB, cursor = OpenDBConnection()
    cursor.execute(f"SELECT * FROM places WHERE placeid = (%s)", (str(placeid),))
    results = cursor.fetchone()
    cursor.close()
    if results is None:
        return None
    return {"placeid":placeid,"name":results[1],"thumbnaillink":results[2],"isblacklisted":bool(results[4])}

def get_detailed_game_info(placeid):
    MYSQLDB, cursor = OpenDBConnection()
    cursor.execute(f"SELECT * FROM places WHERE placeid = (%s)", (str(placeid),))
    results = cursor.fetchone()
    cursor.close()
    if results is None:
        return None
    return {"placeid":placeid,"name":results[1],"thumbnaillink":results[2],"lastupdated":results[3],"isblacklisted":bool(results[4])}

def findserverbylinkcode(linkcode):
    # Finds server by linkcode
    MYSQLDB, cursor = OpenDBConnection()
    MYSQLDB.commit()
    cursor.execute(f"SELECT * FROM vipservers WHERE serverlinkcode = (%s)", (linkcode,))
    result = cursor.fetchone()
    cursor.close()
    return result

def create_new_game(placeid):
    MYSQLDB, cursor = OpenDBConnection()
    req = requests.get(f"https://api.roblox.com/universes/get-universe-containing-place?placeid={str(placeid)}")
    if req.status_code == 200:
        universeid = req.json()["UniverseId"]
        thumbnailreq = requests.get(f"https://thumbnails.roblox.com/v1/games/icons?universeIds={str(universeid)}&size=512x512&format=Png&isCircular=false")
        thumbnaillink = None
        if thumbnailreq.status_code == 200:
            if "imageUrl" in thumbnailreq.json()["data"][0]:
                thumbnaillink = thumbnailreq.json()["data"][0]["imageUrl"]
            
        # Get game name
        gamereq = requests.get(f"https://games.roblox.com/v1/games?universeIds={str(universeid)}")
        gamename = None
        if gamereq.status_code == 200:
            if len(gamereq.json()["data"]) >= 1:
                gamename = gamereq.json()["data"][0]["name"]
            
        if gamename is not None and thumbnaillink is not None:
            cursor.execute("INSERT INTO places (`placeid`,`name`,`thumbnaillink`,`lastupdated`,`isblacklisted`) VALUES (%s,%s,%s,%s,%s);", (placeid, gamename, thumbnaillink, str(time.time()), 0))
            MYSQLDB.commit()
    cursor.close()

def createnewvipserver(placeid,serverlinkcode,uploaderhash):
    if get_game_info(placeid) is None:
        create_new_game(placeid)
    # Creates new vipserver in vipservers table (serverid 48 random string character, placeid TINYTEXT, serverlinkcode MEDIUMTEXT, uploaded INT(timestamp), lastchecked INT(timestamp), uploaderhash (64 CHAR), isvalid BOOL)
    MYSQLDB, cursor = OpenDBConnection()
    serverid = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(48))
    cursor.execute("INSERT INTO vipservers (`serverid`,`placeid`,`serverlinkcode`,`uploaded`,`lastchecked`,`uploaderhash`,`isvalid`) VALUES (%s,%s,%s,%s,%s,%s,%s);", (serverid, placeid, serverlinkcode, int(time.time()), int(time.time()), uploaderhash, 1))
    MYSQLDB.commit()
    cursor.close()
    return serverid

def gettotalservercount():
    MYSQLDB, cursor = OpenDBConnection()
    cursor.execute("SELECT COUNT(*) FROM vipservers WHERE isvalid = 1")
    result = cursor.fetchone()[0]
    cursor.close()
    return result

def gettotalgamecount():
    MYSQLDB, cursor = OpenDBConnection()
    cursor.execute("SELECT COUNT(*) FROM places WHERE isblacklisted = 0 AND ( SELECT COUNT(*) FROM vipservers WHERE vipservers.placeid = places.placeid AND vipservers.isvalid = 1) > 0")
    result = cursor.fetchone()[0]
    cursor.close()
    return result

def getgamelist():
    # Gets list of places from places which is not blacklisted and sorts by server count in vipservers table which matches placeid and limit the results to 64
    MYSQLDB, cursor = OpenDBConnection()
    MYSQLDB.commit()
    cursor.execute(f"SELECT * FROM places WHERE isblacklisted = 0 ORDER BY (SELECT COUNT(*) FROM vipservers WHERE placeid = places.placeid AND isvalid = 1) DESC LIMIT 64")
    result = cursor.fetchall()
    cursor.close()
    return result