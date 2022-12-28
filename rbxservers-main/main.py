from flask import *
import mysql.connector
import os
import timeago
from datetime import datetime
import re
import time
import base64
import random
import json
import hashlib
import requests
import string
import libraries.mysql_manager as mysql_manager
import blueprints.admin
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

app = Flask(__name__,template_folder='templates',static_folder='static')
app.register_blueprint(blueprints.admin.admin_blueprint)

with open("./data/cookies.txt", "r") as f:
    cookies = f.readlines()

def GetOriginalIP(requestobj):
    if "Cf-Connecting-Ip" in requestobj.headers:
        return requestobj.headers["Cf-Connecting-Ip"]
    else:
        return requestobj.remote_addr

def GethashedIP(requestobj):
    OriginalIP = GetOriginalIP(requestobj)
    hash_object = hashlib.sha256(OriginalIP.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig

def getrandomcookie():
    cookie = random.choice(cookies).strip()
    req = requests.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": cookie}, headers={"X-CSRF-TOKEN": requests.post(f"https://auth.roblox.com/v1/usernames/validate").headers["x-csrf-token"]})
    if req.status_code == 200:
        return cookie
    else:
        print("invalid cookie")
        return getrandomcookie()

@app.route("/ads.txt",methods=["GET"])
def adstxt():
    return send_from_directory("./data","ads.txt")

@app.errorhandler(404)
def not_found(error):
    return render_template('notfound404.html'), 404

HomePageServerCount = 0
HomePageGameCount = 0
HomePageLastRefresh = 0

@app.route("/",methods=["GET"])
def rootroute():
    global HomePageServerCount
    global HomePageGameCount
    global HomePageLastRefresh

    if time.time() - HomePageLastRefresh > 120:
        HomePageServerCount = mysql_manager.gettotalservercount()
        HomePageGameCount = mysql_manager.gettotalgamecount()
        HomePageLastRefresh = time.time()

    return render_template("index.html",servercount=str(HomePageServerCount),gamecount=str(HomePageGameCount))
@app.route("/search",methods=["GET","POST"])
def searchroute():
    return render_template("search.html")
@app.route('/privacy',methods=["GET","POST"])
def privacy():
    return render_template("privacy.html")
@app.route('/terms',methods=["GET","POST"])
def terms():
    return render_template("terms.html")

@app.route("/servers/<serverid>",methods=["GET"])
def serverroute(serverid):
    server = mysql_manager.get_server_info(serverid)
    if server is None:
        return render_template("notfound404.html"), 404
    else:
        if server["isvalid"]:
            return redirect(f"https://www.roblox.com/games/{str(server['placeid'])}?privateServerLinkCode={str(server['serverlinkcode'])}", code=302)
        else:
            return render_template("notvalid.html"), 404

@app.route("/api/search",methods=["POST"])
def searchapi():
    jsonpayload = request.get_json()
    if "link" in jsonpayload:
        placeidregex = r"\/games\/(\d*)?"
        placeid = re.search(placeidregex, jsonpayload["link"])
        if placeid is None:
            return jsonify({"status":"error","message":"No placeid found in link"}), 400
        placeid = placeid.group(1)

        if mysql_manager.get_game_info(placeid) is None:
            mysql_manager.create_new_game(placeid)
        return jsonify({"success":True,"gamelink":f"/games/{str(placeid)}"}), 200

@app.route("/games/<placeid>",methods=["GET","POST"])
def gamepage(placeid):
    try:
        int(placeid)
    except Exception:
        
        return render_template("notfound404.html"), 404
    gameinfo = mysql_manager.get_game_info(placeid)
    workerinfo = []
    if gameinfo is None:
        if mysql_manager.get_game_info(placeid) is None:
            mysql_manager.create_new_game(placeid)
        return render_template("notfound404.html"), 404
    if gameinfo["isblacklisted"]:
        return render_template("gamelist.html",
            place_name = gameinfo["name"],
            place_thumbnaillink = gameinfo["thumbnaillink"],
            server_list = """
            <div class="alert alert-danger text-start" role="alert" >
                This game has been blacklisted from uploading VIP servers
            </div>
            """,
            servercount = "?",
            workerinfo=base64.b64encode(json.dumps(workerinfo).encode("ascii")).decode('ascii')
        ), 200
    serverlist = mysql_manager.get_server_list(placeid)
    servercount = mysql_manager.get_server_count(placeid)
    serverlistcontent = ""
    serversplacedcount = 0
    adscount = 0
    for server in serverlist:
        dt_obj = datetime.fromtimestamp(server[3]).strftime('%d / %m / %y')
        serverlistcontent += f"""
        <div class="card card-hover-sm mt-2" style="background-color: rgb(36, 36, 36);">
            <a target="_blank" href="/servers/{server[0]}" class="nav-link">
                <div class="game-card card-body d-md-flex align-items-center p-3 text-center">
                    <h4>{server[2]}</h4>
                        <div class="d-flex me-md-3 flex-fill justify-content-center justify-content-md-end">
                            <h6 class="card-subtitle text-secondary">Last checked <p class="text-primary">{timeago.format(datetime.fromtimestamp(int(server[4])))}</p></h6>
                            <h6 class="card-subtitle text-secondary ms-4">Uploaded on <p class="text-primary">{str(dt_obj)}</p></h6>
                        </div>
                    </div>
                </a>
            </div>
        """
        serversplacedcount += 1
        if serversplacedcount % 8 == 0 and adscount <= 2:
            serverlistcontent += """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5647909494567068"
     crossorigin="anonymous"></script>
<!-- GameListAds -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-5647909494567068"
     data-ad-slot="4796563621"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
"""
            adscount += 1
        workerinfo.append({
            "a":server[0],
            "b":server[2],
            "c": str(dt_obj),
            "d": timeago.format(datetime.fromtimestamp(int(server[4])))
        })
    
    if servercount == 0:
        serverlistcontent = """
            <div class="alert alert-danger text-start" role="alert" >
                This game has no VIP servers
            </div>
        """

    return render_template("gamelist.html",
        place_name = gameinfo["name"],
        place_thumbnaillink = gameinfo["thumbnaillink"],
        server_list = serverlistcontent,
        servercount = str(servercount),
        gamelink = f"https://roblox.com/games/{str(placeid)}/rbxservers",
        workerinfo=base64.b64encode(json.dumps(workerinfo).encode("ascii")).decode('ascii')
    ), 200

GameSectionContent = ""
GameListLastRefresh = 0

@app.route("/game-list",methods=["GET","POST"])
def serverlist():
    global GameSectionContent
    global GameListLastRefresh

    if time.time() - GameListLastRefresh > 120:
        GameSectionContent = ""
        PlaceList = mysql_manager.getgamelist()
        MYSQLDB, cursor = mysql_manager.OpenDBConnection()
        MYSQLDB.commit()
        gamecount = 0
        for place in PlaceList:
            cursor.execute(f"SELECT COUNT(*) FROM vipservers WHERE placeid = (%s) AND isvalid = 1", (str(place[0]),))
            ServerCount = cursor.fetchone()[0]
            if "onload" not in place[1].lower() and "srcset" not in place[1].lower() and "onerror" not in place[1].lower() and "http" not in place[1].lower() and "&#61;" not in place[1].lower() and "&#x3D;" not in place[1].lower() and "&equals;" not in place[1].lower() and "=" not in place[1].lower():
                GameSectionContent += f"""
                    <div class="col-6 col-lg-3 ps-1 pe-1 pb-1 pt-1">
                        <div class="card card-hover" style="background-color: rgb(31,31,31);">
                            <a href="/games/{str(place[0])}" class="nav-link">
                                <img src="{place[2]}" class="card-img-top" alt="{place[1]}">
                                <div class="card-body">
                                <h5 class="card-title text-truncate">{place[1]}</h5>
                                <p class="card-subtitle text-secondary">{str(ServerCount)} Servers</p>
                                </div>
                            </a>
                        </div>
                    </div>
                """
                gamecount += 1
            
            if gamecount % 8 == 0:
                GameSectionContent += """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5647909494567068"
     crossorigin="anonymous"></script>
<!-- GameListAds -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-5647909494567068"
     data-ad-slot="1978828592"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
"""
                #adspotsplaced += 1
        cursor.close()
        GameListLastRefresh = time.time()

    return render_template("serverlist.html", GameSectionContent=GameSectionContent)
@app.route("/share-vip",methods=["GET","POST"])
def sharevip():
    return render_template("sharevip.html")
@app.route("/discord",methods=["GET","POST"])
def discordpage():
    return render_template("discord.html")

@app.route("/api/share-vip",methods=["POST"])
def sharevipapi():
    payload = request.get_json()
    if "link" not in payload:
        return jsonify({"status":"error","message":"No link provided"}), 400
    
    placeidregex = r"\/games\/(\d*)?"
    placeid = re.search(placeidregex, payload["link"])
    if placeid is None:
        return jsonify({"status":"error","message":"No placeid found in link"}), 400
    placeid = placeid.group(1)

    serverlinkcoderegex = r"\?privateServerLinkCode=([\w-]*)"
    serverlinkcode = re.search(serverlinkcoderegex, payload["link"])
    if serverlinkcode is None:
        return jsonify({"status":"error","message":"No serverlinkcode found in link"}), 400
    serverlinkcode = serverlinkcode.group(1)
    gameinfo = mysql_manager.get_game_info(placeid)
    if gameinfo is not None:
        if gameinfo["isblacklisted"]:
            return jsonify({"status":"error","message":"This game is blacklisted"}), 400
    if mysql_manager.findserverbylinkcode(serverlinkcode) is not None:
        return jsonify({"status":"error","message":"Server already exists"}), 400
    Cookie = getrandomcookie()
    vipserverreq = requests.get(
        url=f"https://www.roblox.com/games/{placeid}?privateServerLinkCode={serverlinkcode}",
        cookies={
            ".ROBLOSECURITY": Cookie
        },
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        }
    )
    if "Roblox.GameLauncher.joinPrivateGame" in vipserverreq.text:

        if mysql_manager.findserverbylinkcode(serverlinkcode) is not None:
            return jsonify({"status":"error","message":"Server already exists"}), 400

        req = requests.get(f"https://www.roblox.com/games/{str(placeid)}")
        pricefinderregex = r"data-private-server-price=\"(\d*)\""
        pricefinder = re.search(pricefinderregex, req.text)
        if pricefinder is None:
            return jsonify({"status":"error","message":"Unable to get game info try again later"}), 400
        price = pricefinder.group(1)
        server_count = mysql_manager.get_server_count(placeid)

        if price == 0 and server_count >= 50:
            return jsonify({"status":"error","message":"This game has reached its server limit"}), 400
        elif server_count >= 500:
            return jsonify({"status":"error","message":"This game has reached its server limit"}), 400
        serverid = mysql_manager.createnewvipserver(placeid,serverlinkcode,GethashedIP(request))
        return jsonify({"status":"success","message":"New server created successfully!", "serverid":serverid, "gamename":gameinfo["name"]}), 200
    else:
        return jsonify({"status":"error","message":"Invalid VIP server"}), 400

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=8080
    )