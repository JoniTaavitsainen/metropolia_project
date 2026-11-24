import hashlib
import hmac
import secrets

import mysql.connector

import sql


def _hash_password(password):
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 600_000
    )
    return f"{salt.hex()}${password_hash.hex()}"


def _password_matches(password, stored_password):
    try:
        salt_hex, hash_hex = stored_password.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
    except (ValueError, TypeError):
        return False

    actual_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 600_000
    )
    return hmac.compare_digest(actual_hash, expected_hash)


def create_user(name, password):
    if not name or not password:
        return False, "Käyttäjänimi ja salasana vaaditaan."

    password_hash = _hash_password(password)
    cursor = sql.connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO account (screen_name, password) VALUES (%s, %s)",
            (name, password_hash),
        )
        sql.connection.commit()
    except mysql.connector.Error as error:
        if error.errno == 1062:
            return False, "Käyttäjänimi on jo käytössä."
        return False, f"Käyttäjän luominen epäonnistui. {error.msg}"
    finally:
        cursor.close()

    return True, "Käyttäjä luotiin onnistuneesti."


def authenticate_user(name, password):
    cursor = sql.connection.cursor()
    try:
        cursor.execute(
            "SELECT password FROM account WHERE screen_name = %s", (name,)
        )
        result = cursor.fetchone()
    finally:
        cursor.close()

    if result and _password_matches(password, result[0]):
        return True
    return False