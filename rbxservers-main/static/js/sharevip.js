async function Main() {
    var searchbutton = document.getElementById("vipserverlink-button");
    searchbutton.onclick = async function() {
        var inputfield = document.getElementById("vipserverlink-form-input");
        var gamelink = inputfield.value;
        searchbutton.disabled = true
        inputfield.disabled = true;
        fetch(
            '/api/share-vip',{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'link': gamelink
                })
            }
        ).then(async (response) => {
            var jsondata = await response.json();
            if (jsondata.status === "success") {
                // create new bootstrap success alert in alertlist with close button
                var alertlist = document.getElementById("alertlist");
                var alert = document.createElement("div");
                alert.role="alert"
                alert.className = "alert alert-success alert-dismissible fade show";
                alert.innerHTML = `<strong>Success!</strong> This VIP server has been uploaded to our database. ( ${jsondata.gamename} )`;
                alert.innerHTML += '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
                alertlist.appendChild(alert);
                // clear input field
                inputfield.value = "";
                inputfield.disabled = false;
                searchbutton.disabled = false;
            } else if (jsondata.status === "error") {
                var alertlist = document.getElementById("alertlist");
                var alert = document.createElement("div");
                alert.role="alert"
                alert.className = "alert alert-danger alert-dismissible fade show";
                alert.innerHTML = `<strong>Error</strong> ${jsondata.message}`;
                alert.innerHTML += '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
                alertlist.appendChild(alert);
                // clear input field
                inputfield.value = "";
                inputfield.disabled = false;
                searchbutton.disabled = false
            }
        }).catch(function(error) {
            searchbutton.disabled = false
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