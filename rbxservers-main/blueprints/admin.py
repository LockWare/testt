from flask import *
import hashlib
import libraries.mysql_manager as mysql_manager
import random
import string
import requests
import time

admin_blueprint = Blueprint('admin', __name__)

def IsValidAdminToken(web_request):
    if web_request.cookies.get('administrator_token') is None:
        return False
    admin_token = web_request.cookies.get('administrator_token')
    hashed_token = hashlib.sha256(admin_token.encode('utf-8')).hexdigest()

    AdminInfo = mysql_manager.findtokenbyhash(hashed_token)
    if AdminInfo is not None:
        return AdminInfo
    else:
        return False

@admin_blueprint.route("/admin/panel",methods=["GET"])
def adminpanelroute():
    if IsValidAdminToken(request) is False:
        return render_template("notfound404.html")
    return render_template("adminpanel.html")

@admin_blueprint.route("/admin/api/searchplaceid",methods=["POST"])
def searchplaceid():
    if IsValidAdminToken(request) is False:
        return render_template("notfound404.html")
    
    JSONPayload = request.get_json()
    if "placeid" not in JSONPayload:
        return jsonify({"reason": "placeid not found in json payload","success":False})
    
    PlaceInfo = mysql_manager.get_detailed_game_info(JSONPayload["placeid"])
    if PlaceInfo is None:
        return jsonify({"reason": "placeid not found in database","success":False})
    
    ServerCount = mysql_manager.get_server_count(JSONPayload["placeid"])
    PlaceInfo["servercount"] = ServerCount

    return jsonify({"success":True,"placeinfo":PlaceInfo})

@admin_blueprint.route("/admin/api/actions/blackliststatus",methods=["POST"])
def blackliststatus():
    admininfo = IsValidAdminToken(request)
    if admininfo is False:
        return render_template("notfound404.html")
    
    if admininfo["adminlevel"] <= 1:
        return jsonify({"reason": "insufficient permission","success":False})
    
    JSONPayload = request.get_json()
    if "placeid" not in JSONPayload:
        return jsonify({"reason": "placeid not found in json payload","success":False})
    if "status" not in JSONPayload:
        return jsonify({"reason": "status not found in json payload","success":False})
    
    mysql_manager.setblackliststatus(JSONPayload["placeid"],JSONPayload["status"])
    return jsonify({"success":True,"reason":"Successfully updated game blacklist status"})

@admin_blueprint.route("/admin/api/actions/wipeplace",methods=["POST"])
def wipeplace():
    admininfo = IsValidAdminToken(request)
    if admininfo is False:
        return render_template("notfound404.html")
    
    if admininfo["adminlevel"] < 3:
        return jsonify({"reason": "Insufficient permissions, requires admin level 3.","success":False})
    
    JSONPayload = request.get_json()
    if "placeid" not in JSONPayload:
        return jsonify({"reason": "placeid not found in json payload","success":False})
    
    MYSQLDB, cursor = mysql_manager.OpenDBConnection()
    serverlist = mysql_manager.getallservers(JSONPayload["placeid"])
    for server in serverlist:
        cursor.execute("INSERT INTO deletedservers (`serverid`,`placeid`,`serverlinkcode`,`uploaded`,`lastchecked`,`uploaderhash`,`isvalid`,`adminhash`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);", (server[0], server[1], server[2], server[3], server[4], server[5], server[6], admininfo["tokenhash"]))
        cursor.execute("DELETE FROM vipservers WHERE serverid = %s;", (server[0],))
    MYSQLDB.commit()
    cursor.close()

    return jsonify({"success":True,"reason":"Successfully wiped game"})

@admin_blueprint.route("/admin/api/actions/recheckall",methods=["POST"])
def recheckall():
    admininfo = IsValidAdminToken(request)
    if admininfo is False:
        return render_template("notfound404.html")

    JSONPayload = request.get_json()
    if "placeid" not in JSONPayload:
        return jsonify({"reason": "placeid not found in json payload","success":False})
    
    MYSQLDB, cursor = mysql_manager.OpenDBConnection()
    cursor.execute("UPDATE vipservers SET lastchecked = 0 WHERE placeid = %s", (JSONPayload["placeid"],))
    MYSQLDB.commit()
    cursor.close()

    return jsonify({"success":True,"reason":"Successfully queued all vip servers to be revalidated"})

@admin_blueprint.route("/admin/api/searchserverid",methods=["POST"])
def searchserverid():
    if IsValidAdminToken(request) is False:
        return render_template("notfound404.html")
    
    JSONPayload = request.get_json()
    if "serverid" not in JSONPayload:
        return jsonify({"reason": "serverid not found in json payload","success":False})
    
    ServerInfo = mysql_manager.get_server_info(JSONPayload["serverid"])
    if ServerInfo is None:
        return jsonify({"reason": "serverid not found in database","success":False})
    
    PlaceInfo = mysql_manager.get_game_info(ServerInfo["placeid"])
    ServerInfo["gamename"] = PlaceInfo["name"]
    return jsonify({"success":True,"serverinfo":ServerInfo})

@admin_blueprint.route("/admin/api/actions/recheckserverid",methods=["POST"])
def recheckserverid():
    admininfo = IsValidAdminToken(request)
    if admininfo is False:
        return render_template("notfound404.html")
    
    JSONPayload = request.get_json()
    if "serverid" not in JSONPayload:
        return jsonify({"reason": "serverid not found in json payload","success":False})
    
    MYSQLDB, cursor = mysql_manager.OpenDBConnection()
    cursor.execute("UPDATE vipservers SET lastchecked = 0 WHERE serverid = %s", (JSONPayload["serverid"],))
    MYSQLDB.commit()
    cursor.close()

    return jsonify({"success":True,"reason":"Successfully queued vip server to be revalidated"})

@admin_blueprint.route("/admin/api/actions/deleteserver",methods=["POST"])
def deleteserver():
    admininfo = IsValidAdminToken(request)
    if admininfo is False:
        return render_template("notfound404.html")
    
    if admininfo["adminlevel"] < 2:
        return jsonify({"reason": "Insufficient permissions, requires admin level 2.","success":False})

    JSONPayload = request.get_json()
    if "serverid" not in JSONPayload:
        return jsonify({"reason": "serverid not found in json payload","success":False})
    
    MYSQLDB, cursor = mysql_manager.OpenDBConnection()
    ServerInfo = mysql_manager.get_server_info(JSONPayload["serverid"])
    cursor.execute("INSERT INTO deletedservers (`serverid`,`placeid`,`serverlinkcode`,`uploaded`,`lastchecked`,`uploaderhash`,`isvalid`,`adminhash`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);", (ServerInfo["serverid"], ServerInfo["placeid"], ServerInfo["serverlinkcode"], ServerInfo["uploaded"], ServerInfo["lastchecked"], ServerInfo["uploaderhash"], ServerInfo["isvalid"], admininfo["tokenhash"]))
    cursor.execute("DELETE FROM vipservers WHERE serverid = %s;", (JSONPayload["serverid"],))
    MYSQLDB.commit()
    cursor.close()

    return jsonify({"success":True,"reason":"Successfully deleted server"})

@admin_blueprint.route('/admin/api/actions/newtoken', methods=['POST'])
def newtoken():
    admininfo = IsValidAdminToken(request)
    if admininfo is False:
        return render_template("notfound404.html")
    if admininfo["adminlevel"] < 3:
        return jsonify({"reason": "Insufficient permissions, requires admin level 3.","success":False})
    
    JSONPayload = request.get_json()
    if "adminlevel" not in JSONPayload:
        return jsonify({"reason": "adminlevel not found in json payload","success":False})
    if "adminname" not in JSONPayload:
        return jsonify({"reason": "adminname not found in json payload","success":False})
    adminname = JSONPayload["adminname"]
    if adminname == "":
        return jsonify({"reason": "Nickname cannot be empty","success":False})
    if len(adminname) < 3:
        return jsonify({"reason": "Nickname too short, needs to be at least 3 characters","success":False})
    if len(adminname) > 32:
        return jsonify({"reason": "Nickname too long, needs to be at most 32 characters","success":False})

    # generate 256 character long string which includes uppercase and lowercase letters and numbers
    token = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(256))
    tokenhash = hashlib.sha256(token.encode()).hexdigest()
    MYSQLDB, cursor = mysql_manager.OpenDBConnection()
    cursor.execute("INSERT INTO admintokens (`tokenid`,`tokenhash`,`created`,`creatorhash`,`adminlevel`,`nickname`) VALUES (0,%s,%s,%s,%s,%s);", (tokenhash, int(time.time()), admininfo["tokenhash"], JSONPayload["adminlevel"], JSONPayload["adminname"]))
    MYSQLDB.commit()
    cursor.close()

    return jsonify({"success":True,"reason":"Successfully created new token","token":token})

@admin_blueprint.route('/admin/api/actions/refreshgamedata', methods=['POST'])
def refreshgamedata():
    admininfo = IsValidAdminToken(request)
    if admininfo is False:
        return render_template("notfound404.html")

    jsonpayload = request.get_json()
    if "placeid" not in jsonpayload:
        return jsonify({"reason": "Placeid not found in payload","success":False})

    placeid = jsonpayload["placeid"]

    MYSQLDB, cursor = mysql_manager.OpenDBConnection()
    req = requests.get(f"https://api.roblox.com/universes/get-universe-containing-place?placeid={str(placeid)}")
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
            cursor.execute(f"UPDATE places SET name = (%s), thumbnaillink = (%s), lastupdated = (%s) WHERE placeid = (%s)", (gamename,thumbnaillink,str(time.time()),str(placeid)))
            MYSQLDB.commit()
        else:
            return jsonify({"success":False,"reason":"Unable to gather all info for placeid "+str(placeid)})
    else:
        return jsonify({"success":False,"reason":"Roblox returned status code "+ str(req.status_code) +" when trying to get universe id for placeid "+str(placeid)})

    return jsonify({"success":True,"reason":"Successfully refreshed game data"})