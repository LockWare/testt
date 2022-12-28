var CurrentModal = null;
var TargetPlaceId = null;
var TargetServerId = null;

function CreateModal (Title, Content, YesText, NoText, callback) {
    if (CurrentModal != null) {
        CurrentModal.remove();
    }

    CurrentModal = document.createElement("div");
    CurrentModal.innerHTML = `
    <div class="modal fade" data-bs-backdrop="static" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">${Title}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <p style="word-wrap:break-word;">${Content}</p>
            </div>
            <div class="modal-footer">
                <button type="button" id="modal-cancel-button" class="btn btn-secondary" data-bs-dismiss="modal">${NoText}</button>
                <button type="button" id="modal-success-button" class="btn btn-primary" data-bs-dismiss="modal">${YesText}</button>
            </div>
            </div>
        </div>
    </div>
    `
    CurrentModal.querySelector('#modal-success-button').onclick = callback;
    document.body.appendChild(CurrentModal);

    var BootModal = new bootstrap.Modal(CurrentModal.querySelector('.modal'));
    BootModal.show();
}

function ShowAlertModal (Title,Content) {
    if (CurrentModal != null) {
        CurrentModal.remove();
    }

    CurrentModal = document.createElement("div");
    CurrentModal.innerHTML = `
    <div class="modal fade" data-bs-backdrop="static" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">${Title}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <p style="word-wrap:break-word;">${Content}</p>
            </div>
            <div class="modal-footer">
                <button type="button" id="modal-cancel-button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
            </div>
        </div>
    </div>
    `
    document.body.appendChild(CurrentModal);

    var BootModal = new bootstrap.Modal(CurrentModal.querySelector('.modal'));
    BootModal.show();
}

async function GetTimestamp(Epoch) {
    var date = new Date(Epoch);
    var timestamp = date.toLocaleString();
    return timestamp;
}

async function Main() {
    const PlaceIdLookupButton = document.getElementById("placeid-button");
    const PlaceIdInputField = document.getElementById("placeidforminput");

    const PlaceIdResults = document.getElementById("placeid-results");
    this.document.head.appendChild(PlaceIdResults)
    const PlaceIdRecheckBtn = document.getElementById("placeid-recheck");
    const PlaceIdRefreshInfo = document.getElementById("placeid-gameinfo");
    const PlaceIdWipeAllBtn = document.getElementById("placeid-wipe");
    const PlaceIdBlacklistBtn = document.getElementById("placeid-blacklist");
    const PlaceIdUnblacklistBtn = document.getElementById("placeid-unblacklist");
    const PlaceIdServerCountText = document.getElementById("placeid-servercount");
    const PlaceIdLastRefreshText = document.getElementById("placeid-lastrefresh");
    const PlaceIdGameNameText = document.getElementById("placeid-gamename");
    const PlaceIdIdText = document.getElementById("placeid-id");
    const PlaceIdIsBlacklisted = document.getElementById("placeid-isblacklisted");

    const ServerIdLookupButton = document.getElementById("serverid-button");
    const ServerIdInputField = document.getElementById("serveridforminput");

    const ServerIdResults = document.getElementById("serverid-results");
    this.document.head.appendChild(ServerIdResults)
    const ServerIdRecheckBtn = document.getElementById("serverid-recheck");
    const ServerIdDeleteBtn = document.getElementById("serverid-delete");
    const ServerIdUploadedOnText = document.getElementById("serverid-uploaded");
    const ServerIdLastCheckedText = document.getElementById("serverid-checked");
    const ServerIdUploaderText  = document.getElementById("serverid-uploader");
    const ServerIdPlaceText = document.getElementById("serverid-place");
    const ServerIdLinkCodeText = document.getElementById("serverid-linkcode");
    const ServerIdIdText = document.getElementById("serverid-internal");
    const ServerIdIsValid = document.getElementById("serverid-isvalid");

    const GenerateTokenButton = document.getElementById("generate-token-btn");
    const GenerateTokenNicknameField = document.getElementById("generate-token-nickname");
    const GenerateTokenLevelSelect = document.getElementById("generate-token-level-select");

    const PlaceIdResultsParent = document.getElementById("place")
    const ServerIdResultsParent = document.getElementById("privateserver")

    const PlaceButton = document.getElementById("placebutton")

    GenerateTokenButton.onclick = async function () {
        GenerateTokenButton.disabled = true;
        GenerateTokenButton.textContent = "Generating...";

        fetch("/admin/api/actions/newtoken",{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                adminname: GenerateTokenNicknameField.value,
                adminlevel: parseInt(GenerateTokenLevelSelect.options[GenerateTokenLevelSelect.selectedIndex].value)
            })
        }).then(async function (res) {
            GenerateTokenButton.disabled = false;
            GenerateTokenButton.textContent = "";
            var jsonresponse = await res.json();
            if (jsonresponse.success) {
                ShowAlertModal("Successfully generated token",`Generated token: <b>${jsonresponse.token}</b>`);
            } else {
                ShowAlertModal("Error","Failed to generate token. Reason: <b>" + jsonresponse.reason + "</b>");
            }
        })
    }

    PlaceIdLookupButton.onclick = async function () {
        PlaceIdLookupButton.disabled = true;
        PlaceIdLookupButton.textContent = "Searching";
        document.head.appendChild(PlaceIdResults);

        fetch("/admin/api/searchplaceid",{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                placeid: parseInt(PlaceIdInputField.value)
            })
        }).then(async function (res) {
            PlaceIdLookupButton.disabled = false;
            PlaceIdLookupButton.textContent = "Search";
            var jsonresponse = await res.json();
            if (jsonresponse.success) {
                TargetPlaceId = parseInt(PlaceIdInputField.value);
                PlaceIdGameNameText.textContent = jsonresponse.placeinfo.name
                PlaceIdServerCountText.textContent = jsonresponse.placeinfo.servercount;
                PlaceIdLastRefreshText.textContent = await GetTimestamp(jsonresponse.placeinfo.lastupdated*1000);
                PlaceIdIdText.textContent = jsonresponse.placeinfo.placeid;
                if (jsonresponse.placeinfo.isblacklisted) {
                    PlaceIdIsBlacklisted.textContent = "Game is blacklisted";
                    PlaceIdIsBlacklisted.style.color = "red";
                } else {
                    PlaceIdIsBlacklisted.textContent = "Game is not blacklisted";
                    PlaceIdIsBlacklisted.style.color = "green";
                }

                PlaceIdResultsParent.appendChild(PlaceIdResults)
            } else {
                ShowAlertModal("Error","Failed to lookup place id. Reason: <b>" + jsonresponse.reason + "</b>");
            }
        })
    }

    PlaceIdRecheckBtn.onclick = async function () {
        // Disable all the children elements of the PlaceIdRecheckBtn parent
        for (var i = 0; i < PlaceIdRecheckBtn.parentElement.children.length; i++) {
            PlaceIdRecheckBtn.parentElement.children[i].disabled = true;
        }

        fetch("/admin/api/actions/recheckall",{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                placeid: TargetPlaceId
            })
        }).then(async function (res) {
            // Enable all the children elements of the PlaceIdRecheckBtn parent
            for (var i = 0; i < PlaceIdRecheckBtn.parentElement.children.length; i++) {
                PlaceIdRecheckBtn.parentElement.children[i].disabled = false;
            }
            var jsonresponse = await res.json();
            if (jsonresponse.success) {
                ShowAlertModal("Success","Successfully queued all servers to be revalidated.");
            } else {
                ShowAlertModal("Error","Failed to recheck place id. Reason: <b>" + jsonresponse.reason + "</b>");
            }
        })
    }

    PlaceIdRefreshInfo.onclick = async function() {
        for (var i = 0; i < PlaceIdRecheckBtn.parentElement.children.length; i++) {
            PlaceIdRecheckBtn.parentElement.children[i].disabled = true;
        }
        fetch("/admin/api/actions/refreshgamedata",{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                placeid: TargetPlaceId
            })
        }).then(async function (res) {
            // Enable all the children elements of the PlaceIdRecheckBtn parent
            for (var i = 0; i < PlaceIdRecheckBtn.parentElement.children.length; i++) {
                PlaceIdRecheckBtn.parentElement.children[i].disabled = false;
            }
            var jsonresponse = await res.json();
            if (jsonresponse.success) {
                ShowAlertModal("Success","Successfully refreshed game data.");
            } else {
                ShowAlertModal("Error","Failed to refresh place. Reason: <b>" + jsonresponse.reason + "</b>");
            }
        })
    }

    PlaceIdWipeAllBtn.onclick = async function () {
        CreateModal("Are you sure?", "Are you sure you want to <b>wipe all</b> servers for this place? This action will be logged!!", "Wipe All", "Cancel", async function () {
            // Disable all the children elements of the PlaceIdRecheckBtn parent
            for (var i = 0; i < PlaceIdRecheckBtn.parentElement.children.length; i++) {
                PlaceIdRecheckBtn.parentElement.children[i].disabled = true;
            }

            fetch("/admin/api/actions/wipeplace",{
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    placeid: TargetPlaceId
                })
            }).then(async function (res) {
                // Enable all the children elements of the PlaceIdRecheckBtn parent
                for (var i = 0; i < PlaceIdRecheckBtn.parentElement.children.length; i++) {
                    PlaceIdRecheckBtn.parentElement.children[i].disabled = false;
                }
                var jsonresponse = await res.json();
                if (jsonresponse.success) {
                    ShowAlertModal("Success","Successfully wiped all servers for this place.");
                } else {
                    ShowAlertModal("Error","Failed to wipe all servers for this place. Reason: <b>" + jsonresponse.reason + "</b>");
                }
            })
        })
    }

    PlaceIdBlacklistBtn.onclick = async function () {
        CreateModal("Are you sure?", "Are you sure you want to <b>blacklist</b> this place?", "Blacklist", "Cancel", async function () {
            // Disable all the children elements of the PlaceIdRecheckBtn parent
            for (var i = 0; i < PlaceIdRecheckBtn.parentElement.children.length; i++) {
                PlaceIdRecheckBtn.parentElement.children[i].disabled = true;
            }

            fetch("/admin/api/actions/blackliststatus",{
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    placeid: TargetPlaceId,
                    status: true
                })
            }).then(async function (res) {
                // Enable all the children elements of the PlaceIdRecheckBtn parent
                for (var i = 0; i < PlaceIdRecheckBtn.parentElement.children.length; i++) {
                    PlaceIdRecheckBtn.parentElement.children[i].disabled = false;
                }
                var jsonresponse = await res.json();
                if (jsonresponse.success) {
                    ShowAlertModal("Success","Successfully updated blacklist status this place.");
                } else {
                    ShowAlertModal("Error","Failed to blacklist this place. Reason: <b>" + jsonresponse.reason + "</b>");
                }
            })
        })
    }

    PlaceIdUnblacklistBtn.onclick = async function () {
        CreateModal("Are you sure?", "Are you sure you want to <b>unblacklist</b> this place?", "Unblacklist", "Cancel", async function () {
            // Disable all the children elements of the PlaceIdRecheckBtn parent
            for (var i = 0; i < PlaceIdRecheckBtn.parentElement.children.length; i++) {
                PlaceIdRecheckBtn.parentElement.children[i].disabled = true;
            }

            fetch("/admin/api/actions/blackliststatus",{
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    placeid: TargetPlaceId,
                    status: false
                })
            }).then(async function (res) {
                // Enable all the children elements of the PlaceIdRecheckBtn parent
                for (var i = 0; i < PlaceIdRecheckBtn.parentElement.children.length; i++) {
                    PlaceIdRecheckBtn.parentElement.children[i].disabled = false;
                }
                var jsonresponse = await res.json();
                if (jsonresponse.success) {
                    ShowAlertModal("Success","Successfully updated blacklist status this place.");
                } else {
                    ShowAlertModal("Error","Failed to unblacklist this place. Reason: <b>" + jsonresponse.reason + "</b>");
                }
            })
        })
    }

    ServerIdLookupButton.onclick = async function () {
        ServerIdLookupButton.disabled = true;
        ServerIdLookupButton.innerHTML = "Searching";
        document.head.appendChild(ServerIdResults)

        fetch("/admin/api/searchserverid",{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                serverid: ServerIdInputField.value
            })
        }).then(async function (res) {
            ServerIdLookupButton.disabled = false;
            ServerIdLookupButton.innerHTML = "Search";
            var jsonresponse = await res.json();
            if (jsonresponse.success) {
                TargetServerId = ServerIdInputField.value
                ServerIdUploadedOnText.textContent = await GetTimestamp(jsonresponse.serverinfo.uploaded*1000);
                ServerIdLastCheckedText.textContent = await GetTimestamp(jsonresponse.serverinfo.lastchecked*1000);
                ServerIdUploaderText.textContent = jsonresponse.serverinfo.uploaderhash;
                ServerIdPlaceText.innerHTML = jsonresponse.serverinfo.placeid+`( ${jsonresponse.serverinfo.gamename} )`;

                ServerIdPlaceText.onclick = async function() {
                    bootstrap.Tab.getInstance(PlaceButton).show();
                    PlaceIdInputField.value = jsonresponse.serverinfo.placeid;
                    PlaceIdLookupButton.click();
                }

                ServerIdLinkCodeText.textContent = jsonresponse.serverinfo.serverlinkcode;
                ServerIdIdText.textContent = jsonresponse.serverinfo.serverid;

                if (jsonresponse.serverinfo.isvalid) {
                    ServerIdIsValid.textContent = "Server is valid";
                    ServerIdIsValid.style.color = "green";
                } else {
                    ServerIdIsValid.textContent = "Server is not valid";
                    ServerIdIsValid.style.color = "red";
                }

                ServerIdResultsParent.appendChild(ServerIdResults)
            } else {
                ShowAlertModal("Error","Failed to lookup server id. Reason: <b>" + jsonresponse.reason + "</b>");
            }
        })
    }

    ServerIdRecheckBtn.onclick = async function () {
        for (var i = 0; i < ServerIdRecheckBtn.parentElement.children.length; i++) {
            ServerIdRecheckBtn.parentElement.children[i].disabled = true;
        }
        fetch("/admin/api/actions/recheckserverid",{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                serverid: TargetServerId
            })
        }).then(async function (res) {
            for (var i = 0; i < ServerIdRecheckBtn.parentElement.children.length; i++) {
                ServerIdRecheckBtn.parentElement.children[i].disabled = false;
            }
            var jsonresponse = await res.json();
            if (jsonresponse.success) {
                ShowAlertModal("Success","Successfully queued private server to be rechecked.");
            } else {
                ShowAlertModal("Error","Failed to recheck server id. Reason: <b>" + jsonresponse.reason + "</b>");
            }
        })
    }

    ServerIdDeleteBtn.onclick = async function () {
        CreateModal("Are you sure?","Are you sure you want to <b>delete</b> this private server? This action will be logged.","Delete","Cancel",async function() {
            for (var i = 0; i < ServerIdRecheckBtn.parentElement.children.length; i++) {
                ServerIdRecheckBtn.parentElement.children[i].disabled = true;
            }
            fetch("/admin/api/actions/deleteserver",{
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    serverid: TargetServerId
                })
            }).then(async function (res) {
                for (var i = 0; i < ServerIdRecheckBtn.parentElement.children.length; i++) {
                    ServerIdRecheckBtn.parentElement.children[i].disabled = false;
                }
                var jsonresponse = await res.json();
                if (jsonresponse.success) {
                    ShowAlertModal("Success","Successfully deleted private server.");
                } else {
                    ShowAlertModal("Error","Failed to delete private server. Reason: <b>" + jsonresponse.reason + "</b>");
                }
            })
        })
    }
}

if ( document.readyState === "complete") {
    Main()
}
else if ( document.readyState === "interactive") {
    Main()
}
else {
    document.addEventListener("DOMContentLoaded", async function() {
        Main()
    });
}