"use strict";

const form = document.getElementById("auth-form");
const username = document.getElementById("username");
const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirm-password");
const confirmContainer = document.getElementById("confirm-container");
const submitBtn = document.getElementById("submit-btn");
const loginTab = document.getElementById("tab-login");
const registerTab = document.getElementById("tab-register");
const message = document.getElementById("message");

let registerMode = false;

// login ja käyttäjä tunnus luonti vaihto

loginTab.onclick = () => {
    registerMode = false;

    confirmContainer.hidden = true;
    confirmPassword.required = false;

    submitBtn.textContent = "Kirjaudu sisään";

    message.textContent = "";
};

registerTab.onclick = () => {
    registerMode = true;

    confirmContainer.hidden = false;
    confirmPassword.required = true;

    submitBtn.textContent = "Luo uusi käyttäjä";

    message.textContent = "";
};


form.addEventListener("submit", function(event) {

    event.preventDefault();

    const name = username.value.trim();
    const pass = password.value;

    // säästä tietoa browseriin
    let users = JSON.parse(
        localStorage.getItem("users") || "{}"
    );

    if (registerMode) {

        // tarkistaa salasanaa

        if (pass !== confirmPassword.value) {
            showMessage("Salasanat eivät täsmää!", false);
            return;
        }


        if (users[name]) {
            showMessage("Käyttäjänimi on jo käytössä!", false);
            return;
        }

        // käyttäjä laitetaan local storageen

        users[name] = pass;

        localStorage.setItem("users", JSON.stringify(users));

        showMessage("Käyttäjä luotu!", true);

        // resetoi lomakekentät, kun rekisteröi käyttäjän
        form.reset();

        registerMode = false;
        confirmContainer.hidden = true;
        confirmPassword.required = false;

        submitBtn.textContent = "Kirjaudu sisään";

    } else {

        // tarkistaa jos käyttäjämimi ja salsana ovat samoja

        if (users[name] && users[name] === pass) {

            // käyttäjä tietoo säästetään
            localStorage.setItem("loggedInUser", name);

            showMessage("Kirjautuminen onnistui!", true);

            form.reset();

            // peli vois käynnistää täst

        } else {

            // Handle invalid authentication credentials
            showMessage("Väärä käyttäjänimi tai salasana", false);

        }
    }

});



function showMessage(text, success) {

    message.textContent = text;

    message.className = success ? "ok" : "error";

}
