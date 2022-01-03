//onload do this

onload = function() {
    let endButton = document.getElementById("end-button");

    // if end button is clicked

    endButton.onclick = function() {
        let mainText = document.getElementById("main-text");
        mainText.innerHTML = "<h1>You may now close this window.</h1>";
        endButton.style.display = "none";
    }

}