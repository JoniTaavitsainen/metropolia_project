import os
import re
import secrets
from datetime import timedelta

from flask import Flask, jsonify, request, send_from_directory, session

import sql
from auth import authenticate_user, create_user

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
# Set SECRET_KEY in the environment to keep sessions valid across restarts.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
)

# Dev origins allowed to call the API from another port (e.g. Live Server).
_DEV_ORIGIN = re.compile(r"^http://(localhost|127\.0\.0\.1)(:\d+)?$")


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin", "")
    if _DEV_ORIGIN.match(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Vary"] = "Origin"
    return response


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/<path:_path>", methods=["OPTIONS"])
def preflight(_path):
    return "", 204


def _json_body():
    return request.get_json(silent=True) or {}


def _error(message, status):
    return jsonify(success=False, message=message), status


def _current_account_id():
    return session.get("account_id")


def _require_login():
    """Returns an error response if nobody is logged in, otherwise None."""
    if _current_account_id() is None:
        return _error("Kirjaudu ensin sisään.", 401)
    return None


def _get_account_id_by_name(name):
    row = sql.sql_fetchone(
        "SELECT id FROM account WHERE screen_name = %s", (name,)
    )
    return row[0] if row else None


# ---------- auth ----------

@app.post("/api/register")
def register():
    data = _json_body()
    name = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    ok, message = create_user(name, password)
    return jsonify(success=ok, message=message), (200 if ok else 400)


@app.post("/api/login")
def login():
    data = _json_body()
    name = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not name or not password or not authenticate_user(name, password):
        return _error("Väärä käyttäjänimi tai salasana", 401)

    account_id = _get_account_id_by_name(name)
    if account_id is None:
        return _error("Väärä käyttäjänimi tai salasana", 401)

    session.clear()
    session.permanent = True
    session["account_id"] = account_id
    session["username"] = name
    return jsonify(success=True, message="Kirjautuminen onnistui!", username=name)


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(success=True, message="Kirjauduttu ulos.")


@app.get("/api/me")
def me():
    if _current_account_id() is None:
        return jsonify(success=True, loggedIn=False)
    return jsonify(success=True, loggedIn=True, username=session.get("username"))


# ---------- saves ----------

@app.get("/api/saves")
def list_saves():
    denied = _require_login()
    if denied:
        return denied

    account_id = _current_account_id()
    rows = sql.sql_result(
        "SELECT id, last_played FROM game WHERE account_id = %s "
        "ORDER BY last_played DESC, id DESC",
        (account_id,),
    ) or []
    stats = sql.sql_fetchone(
        "SELECT win, loss FROM account WHERE id = %s", (account_id,)
    )
    return jsonify(
        success=True,
        saves=[
            {"id": game_id, "lastPlayed": str(last_played)}
            for game_id, last_played in rows
        ],
        wins=stats[0] if stats else 0,
        losses=stats[1] if stats else 0,
    )


@app.post("/api/saves")
def new_save():
    denied = _require_login()
    if denied:
        return denied

    game_id = sql.sql_execute(
        "INSERT INTO game (account_id, last_played) VALUES (%s, NOW())",
        (_current_account_id(),),
    )
    return jsonify(success=True, message="Tallennus luotu.", id=game_id), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)