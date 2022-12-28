async function Main() {
    var searchbutton = document.getElementById("gamelink-button");
    searchbutton.onclick = async function() {
        var inputfield = document.getElementById("gamelink-form-input");
        var gamelink = inputfield.value;
        searchbutton.disabled = true
        fetch(
            '/api/search',{
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
            console.log(jsondata)
            if (jsondata.success) {
                console.log(jsondata.gamelink)
                window.location.href = jsondata.gamelink
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