"use strict";

const API_URL = window.location.port === "5000" ? "" : "http://localhost:5000";


const authView = document.getElementById("auth-view");
const savesView = document.getElementById("saves-view");
const gameView = document.getElementById("game-view");

const form = document.getElementById("auth-form");
const username = document.getElementById("username");
const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirm-password");
const confirmContainer = document.getElementById("confirm-container");
const submitBtn = document.getElementById("submit-btn");
const loginTab = document.getElementById("tab-login");
const registerTab = document.getElementById("tab-register");
const message = document.getElementById("message");


const currentUser = document.getElementById("current-user");
const logoutBtn = document.getElementById("logout-btn");
const record = document.getElementById("record");
const saveList = document.getElementById("save-list");
const noSaves = document.getElementById("no-saves");
const newSaveBtn = document.getElementById("new-save-btn");
const savesMessage = document.getElementById("saves-message");


const selectedSave = document.getElementById("selected-save");
const backBtn = document.getElementById("back-btn");

let registerMode = false;



async function api(path, method = "GET", body = null) {
    const options = {
        method: method,
        credentials: "include" // lähettää ja vastaanottaa istuntoevästeen
    };
    if (body !== null) {
        options.headers = { "Content-Type": "application/json" };
        options.body = JSON.stringify(body);
    }
    const response = await fetch(API_URL + path, options);
    return response.json();
}

function showView(view) {
    authView.hidden = view !== "auth";
    savesView.hidden = view !== "saves";
    gameView.hidden = view !== "game";
}

function showMessage(text, success) {
    message.textContent = text;
    message.className = success ? "ok" : "error";
}

function showSavesMessage(text, success) {
    savesMessage.textContent = text;
    savesMessage.className = success ? "ok" : "error";
}

function formatDate(text) {
    // palvelin antaa muodon "2026-11-25 12:30:00"
    const date = new Date(String(text).replace(" ", "T"));
    return isNaN(date) ? String(text) : date.toLocaleString("fi-FI");
}



// login ja käyttäjätunnuksen luonti vaihto

function setLoginMode() {
    registerMode = false;

    confirmContainer.hidden = true;
    confirmPassword.required = false;

    registerTab.hidden = false; // "Luo uusi käyttäjä" näkyy
    loginTab.hidden = true;

    submitBtn.textContent = "Kirjaudu sisään";

    message.textContent = "";
}

function setRegisterMode() {
    registerMode = true;

    confirmContainer.hidden = false;
    confirmPassword.required = true;

    registerTab.hidden = true;
    loginTab.hidden = false; // "Kirjaudu sisään" -nappi takaisin

    submitBtn.textContent = "Luo uusi käyttäjä";

    message.textContent = "";
}

loginTab.onclick = setLoginMode;
registerTab.onclick = setRegisterMode;

form.addEventListener("submit", async function (event) {

    event.preventDefault();

    const name = username.value.trim();
    const pass = password.value;

    // tarkistaa salasanan
    if (registerMode && pass !== confirmPassword.value) {
        showMessage("Salasanat eivät täsmää!", false);
        return;
    }

    submitBtn.disabled = true;

    try {
        const result = await api(
            registerMode ? "/api/register" : "/api/login",
            "POST",
            { username: name, password: pass }
        );

        if (!result.success) {
            showMessage(result.message, false);
        } else if (registerMode) {
            // käyttäjä luotu -> takaisin kirjautumiseen, nimi jää kenttään
            password.value = "";
            confirmPassword.value = "";
            setLoginMode();
            showMessage(result.message + " Kirjaudu nyt sisään.", true);
        } else {
            // resetoi lomakekentät kirjautumisen jälkeen
            form.reset();
            message.textContent = "";
            await openSaves(result.username);
        }
    } catch (error) {
        showMessage("Palvelimeen ei saatu yhteyttä.", false);
    } finally {
        submitBtn.disabled = false;
    }
});




async function openSaves(name) {
    currentUser.textContent = name;
    savesMessage.textContent = "";
    showView("saves");
    await loadSaves();
}

async function loadSaves() {
    try {
        const result = await api("/api/saves");

        if (!result.success) {
            // istunto vanhentunut -> takaisin kirjautumiseen
            showView("auth");
            showMessage(result.message, false);
            return;
        }

        record.textContent = "voittoja: " + result.wins + "  häviöitä: " + result.losses;
        renderSaves(result.saves);
    } catch (error) {
        showSavesMessage("Tallennuksia ei saatu ladattua.", false);
    }
}

function renderSaves(saves) {
    saveList.replaceChildren();
    noSaves.hidden = saves.length > 0;

    saves.forEach(function (save, index) {
        // lista tulee uusin ensin, joten numero lasketaan lopusta
        const number = saves.length - index;

        const item = document.createElement("li");
        const button = document.createElement("button");
        button.type = "button";
        button.className = "save-item";

        const title = document.createElement("span");
        title.className = "title";
        title.textContent = "Tallennus " + number;

        const meta = document.createElement("span");
        meta.className = "meta";
        meta.textContent = "Viimeksi pelattu: " + formatDate(save.lastPlayed);

        button.append(title, meta);
        button.onclick = function () {
            selectSave(save.id, number);
        };

        item.append(button);
        saveList.append(item);
    });
}

function selectSave(id, number) {
    sessionStorage.setItem("selectedSaveId", String(id));
    selectedSave.textContent = "Tallennus " + number;
    showView("game");
}

newSaveBtn.onclick = async function () {
    newSaveBtn.disabled = true;
    try {
        const result = await api("/api/saves", "POST");
        if (result.success) {
            savesMessage.textContent = "";
            await loadSaves();
        } else {
            showSavesMessage(result.message, false);
        }
    } catch (error) {
        showSavesMessage("Palvelimeen ei saatu yhteyttä.", false);
    } finally {
        newSaveBtn.disabled = false;
    }
};

backBtn.onclick = function () {
    showView("saves");
};

logoutBtn.onclick = async function () {
    try {
        await api("/api/logout", "POST");
    } catch (error) {
        // vaikka yhteys katkeaisi, palataan kirjautumiseen
    }
    sessionStorage.removeItem("selectedSaveId");
    setLoginMode();
    showView("auth");
};




// Jos istunto on vielä voimassa (esim. sivu päivitetty), jatketaan suoraan tallennuksiin.
(async function restoreSession() {
    try {
        const result = await api("/api/me");
        if (result.loggedIn) {
            await openSaves(result.username);
            return;
        }
    } catch (error) {
        // palvelin ei vastaa -> näytetään kirjautuminen
    }
    showView("auth");
})();