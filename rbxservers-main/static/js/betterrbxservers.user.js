// ==UserScript==
// @name         BetterRBXServers
// @version      0.2
// @description  Adds Free VIP server list via RBXServers to Roblox!
// @author       FFC#1263 / 1st#5743
// @match        https://*.roblox.com/games/*
// @icon         https://rbxservers.xyz/favicon.ico
// @supportURL   https://rbxservers.xyz/discord
// @updateURL    https://rbxservers.xyz/static/js/betterrbxservers.user.js
// @downloadURL  https://rbxservers.xyz/static/js/betterrbxservers.user.js
// @run-at       document-start
// @connect      funforcheap.cf
// @connect      rbxservers.xyz
// @grant        GM_xmlhttpRequest
// ==/UserScript==

function main() {
    if (location.hash == "#!/game-instances") {
        if (document.getElementsByClassName("section-content-off")[0].innerText != "This experience does not support Private Servers.") { // if game is possible for script
            GM_xmlhttpRequest({
                method: "GET",
                anonymous: true,
                url: "https://rbxservers.xyz/games/" + document.querySelectorAll('[name="twitter:app:url:ipad"]')[0].content.split("robloxmobile://placeID=").join(""), // game id api for rbxservers
                onload() {
                    // since there is no api for rbxservers, we need to manually use the HTML DOM. :( RIP Performance.
                    outputOfServer = document.createElement("div")
                    outputOfServer.innerHTML = this.response // hope rbxservers dont get hacked, xss bad!
                    outputOfServer.style.display = "none" // dont show the user! remember, this was going to be a api request.
                    document.body.appendChild(outputOfServer)
                    // if (!document.getElementsByClassName("col")[0]) { // no vip servers found.
                    //     clearInterval(checkLoop)
                    //     outputOfServer.remove()
                    // }
                    if (this.status == 404) {
                        clearInterval(checkLoop)
                        outputOfServer.remove()
                    }
                    if (!document.getElementById("rbxservers-running-games")) {
                        // preparing the server list.
                        divForElements = document.getElementById("rbx-friends-running-games").cloneNode(true)
                        divForElements.id = "rbxservers-running-games"
                        divForElements.children[0].children[0].children[0].innerText = "RBXServers"

                        // lets cleanup the html a bit.
                        if (divForElements.children[0].children[0].children[1].attributes.disabled) {
                            divForElements.children[0].children[0].children[1].removeAttribute("disabled")
                        }
                        if (divForElements.children[1].children[0]) {
                            divForElements.children[1].children[0].remove()
                        }
                        if (divForElements.children[1]) {
                            divForElements.children[1].remove()
                        }
                        // if (divForElements.children[0].children[1].children[0]) return divForElements.children[0].children[1].children[0].remove()
                        divForElements.children[0].children[0].children[1].onclick = () => {
                            main()
                        }
                    } else {
                        // we gotta delete all list elements because they are already out of date.
                        for (i = 0; i < document.getElementById("rbxservers-main-ul").childNodes.length; i * 2) {
                            document.getElementById("rbxservers-main-ul").childNodes[i].remove()
                        }
                    }

                    runningGameInstancesContainer = document.getElementById("running-game-instances-container")
                    console.log(runningGameInstancesContainer)
                    runningGameInstancesContainer.insertBefore(divForElements, document.getElementById("rbx-friends-running-games"))

                    //document.getElementById("rbx-friends-running-games").appendChild(divForElements)
                    if (!document.getElementById("rbxservers-main-ul")) {
                        var mainUL = document.createElement("ul")
                        mainUL.id = "rbxservers-main-ul"
                        mainUL.className = "card-list"
                        document.getElementById("rbxservers-running-games").appendChild(mainUL)
                    }

                    // show the list.
                    // Currently at this stage, the list should be empty, BUT ready.
                    // btw if someone can lmk of any apis for getting VIP details without getting to complicated that would be great kthx.
                    // NOTED OUT CODE IS FOR FUTURE API IF ADDED!!
                    // servers = JSON.parse('{"RBXServers":[]}')
                    for (i = 0; i < JSON.parse(atob(document.querySelectorAll('[property="workerinfo"]')[0].content)).length; i++) {
                        rbxServersApi = "https://rbxservers.xyz/servers/" + JSON.parse(atob(document.querySelectorAll('[property="workerinfo"]')[0].content))[i].a
                        serverID = JSON.parse(atob(document.querySelectorAll('[property="workerinfo"]')[0].content))[i].b
                        uploadData = JSON.parse(atob(document.querySelectorAll('[property="workerinfo"]')[0].content))[i].c
                        lastChecked = JSON.parse(atob(document.querySelectorAll('[property="workerinfo"]')[0].content))[i].d

                        let serverItem = document.createElement("li")
                        serverItem.className = "col-md-3 col-sm-4 col-xs-6"

                        let serverDiv = document.createElement("div")
                        serverDiv.className = "card-item"


                        let serverDetails = document.createElement("div")
                        serverDetails.className = "rbx-game-server-details game-server-details"
                        serverDiv.appendChild(serverDetails)

                        let serverInfo = document.createElement("div")
                        serverInfo.className = "text-info rbx-game-status rbx-game-server-status text-overflow"
                        serverInfo.style.textAlign = "center"
                        serverInfo.innerText = serverID
                        serverDetails.appendChild(serverInfo)

                        let serverInfo1 = document.createElement("div")
                        serverInfo1.className = "text-info rbx-game-status rbx-game-server-status text-overflow"
                        serverInfo1.style.textAlign = "center"
                        serverInfo1.innerText = "Last checked:\n" + lastChecked
                        serverDetails.appendChild(serverInfo1)

                        let serverInfo2 = document.createElement("div")
                        serverInfo2.className = "text-info rbx-game-status rbx-game-server-status text-overflow"
                        serverInfo2.style.textAlign = "center"
                        serverInfo2.innerText = "Uploaded on: \n" + uploadData
                        serverDetails.appendChild(serverInfo2)

                        let joinBtn = document.createElement("button")
                        joinBtn.type = "button"
                        joinBtn.className = "btn-full-width btn-control-xs rbx-game-server-join game-server-join-btn btn-primary-md btn-min-width"
                        joinBtn.innerText = "Join"
                        joinBtn.onclick = () => {
                            location.replace(rbxServersApi)
                        }
                        serverDiv.appendChild(joinBtn)

                        serverItem.appendChild(serverDiv)

                        document.getElementById("rbxservers-main-ul").appendChild(serverItem)

                        // var div = document.createElement("div");
                        // div.classList.add("serverDiv")
                        // div.style.userSelect = "none"
                        // div.style.width = "100%"
                        // div.style.height = "100px"
                        // div.style.backgroundColor = "#383a3d"
                        // div.style.transition = "0.2s"
                        // div.style.borderRadius = "3px"
                        // div.style.border = "solid"
                        // div.style.borderColor = "#383a3d"
                        // div.style.cursor = "pointer"
                        // div.style.textAlign = "center"
                        // div.style.paddingTop = "5px"
                        // div.style.marginBottom = "10px"
                        // div.onclick = () => {
                        //     location.replace(rbxServersApi)
                        // }
                        // div.innerText = serverID + "\n Last checked: " + lastChecked + "\n Uploaded on: " + uploadData
                        // divForElements.appendChild(div)


                    }
                    // console.log(servers) // response by server with list of current servers for game.
                    // remove the iframe
                    outputOfServer.remove()
                    //document.getElementById("rbx-friends-running-games").appendChild(divForElements)
                }
            })
        }
    }
}

mainloop = setInterval(() => {
    if (document.getElementsByClassName("icon-nav-home")[0]) {
        main()
        checkLoop = setInterval(() => {
            // just incase smt happens, we will check if the div is visible, if not draw it.
            if (((location.hash == "#!/game-instances") || ((document.getElementsByClassName("rbx-tab tab-game-instances active") && document.getElementsByClassName("rbx-tab tab-game-instances active").length > 0))) && (!document.getElementById("rbxservers-running-games")) && (document.getElementsByClassName("section-content-off")[0].innerText != "This experience does not support Private Servers.")) {
                main()
                clearInterval(checkLoop)
            }
        }, 500)
        // Clear ads then run script.
        // if (document.getElementById("Leaderboard-Abp") && document.getElementById("Skyscraper-Abp-Right")) {
        //     document.getElementById("Leaderboard-Abp").remove()
        //     document.getElementById("Skyscraper-Abp-Right").remove()
        // } else if (document.getElementById("Skyscraper-Abp-Right")) {
        //     document.getElementById("Skyscraper-Abp-Right").remove()
        // } else if (document.getElementById("Skyscraper-Abp-Right")) {
        //     document.getElementById("Leaderboard-Abp").remove()
        // }
        clearInterval(mainloop)
    }
}, 750) // Due to roblox loading at diff times during the day we have to do this.