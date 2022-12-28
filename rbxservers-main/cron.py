import requests
import os
from dotenv import load_dotenv, find_dotenv
import mysql.connector
import time
import random
load_dotenv(find_dotenv())

# Connect to SQL database
MYSQLDB = mysql.connector.connect(
    host=os.getenv('MYSQLDATABASE'),
    user=os.getenv('DATABASE_USER'),
    password=os.getenv('DATABASE_PASSWORD'),
    database=os.getenv('MYSQL_SCHEMA'),
    port=os.getenv('DBPORT')
)

# Get list of places which is not blacklisted
cursor = MYSQLDB.cursor()
MYSQLDB.commit()
print("Getting game list")
cursor.execute(f"SELECT * FROM places WHERE isblacklisted = 0")
results = cursor.fetchall()

for place in results:
    # Get universe id

    if time.time() - place[3] >= 172800:
        req = requests.get(f"https://api.roblox.com/universes/get-universe-containing-place?placeid={str(place[0])}")
        if req.status_code == 200:
            universeid = req.json()['UniverseId']
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
                # Update game info in places table
                print(f"updated game info for {place[1]}")
                cursor.execute(f"UPDATE places SET name = (%s), thumbnaillink = (%s), lastupdated = (%s) WHERE placeid = (%s)", (gamename,thumbnaillink,str(time.time()),str(place[0])))
                MYSQLDB.commit()

# Get list of all servers from vipservers table sorted by lastchecked ascending
print("Getting Server list")
cursor.execute(f"SELECT * FROM vipservers ORDER BY lastchecked ASC")
results = cursor.fetchall()

with open("./data/cookies.txt", "r") as f:
    cookies = f.readlines()

def getrandomcookie():
    cookie = random.choice(cookies).strip()
    req = requests.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": cookie}, headers={"X-CSRF-TOKEN": requests.post(f"https://auth.roblox.com/v1/usernames/validate").headers["x-csrf-token"]})
    if req.status_code == 200:
        return cookie
    else:
        print("invalid cookie")
        return getrandomcookie()

Cookie = getrandomcookie()
CookieUsage = 0

for server in results:
    isvalid = bool(server[6])
    if not isvalid:
        if time.time() - server[4] >= 259200:
            vipserverreq = requests.get(
                url=f"https://www.roblox.com/games/{str(server[1])}?privateServerLinkCode={str(server[2])}",
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
                },
                cookies={
                    ".ROBLOSECURITY":Cookie
                }
            )

            if "Roblox.GameLauncher.joinPrivateGame" in vipserverreq.text:
                print(f"{server[0]} is valid")
                cursor.execute(f"UPDATE vipservers SET isvalid = 1, lastchecked = (%s) WHERE serverid = (%s)", (str(time.time()),str(server[0])))
                MYSQLDB.commit()
            else:
                print(f"deleting invalid server {server[0]}")
                cursor.execute(f"DELETE FROM vipservers WHERE serverid = (%s)", (str(server[0]),))
                MYSQLDB.commit()
    else:
        if time.time() - server[4] >= 600:
            vipserverreq = requests.get(
                url=f"https://www.roblox.com/games/{str(server[1])}?privateServerLinkCode={str(server[2])}",
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
                },
                cookies={
                    ".ROBLOSECURITY":Cookie
                }
            )

            if "Roblox.GameLauncher.joinPrivateGame" in vipserverreq.text:
                # set valid to 1 and lastchecked to time.time()
                print(f"{server[0]} is valid")
                cursor.execute(f"UPDATE vipservers SET isvalid = 1, lastchecked = (%s) WHERE serverid = (%s)", (str(time.time()),str(server[0])))
                MYSQLDB.commit()
            else:
                print(f"{server[0]} is invalid")
                cursor.execute(f"UPDATE vipservers SET isvalid = 0, lastchecked = (%s) WHERE serverid = (%s)", (str(time.time()),str(server[0])))
                MYSQLDB.commit()
    if isvalid:
        CookieUsage += 1
    if CookieUsage >= 25:
        break
