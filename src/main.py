from enum import Enum

import waitress
from flask import Flask, request, session

from db import get_user
from src.db import add_user

app = Flask(__name__)


@app.route("/")
def hello_world() -> str:
    return "<p>Hello, World!</p><a href=/link>A linky link!</a>"


@app.post("/login")
def login() -> dict:
    """
    {"username": "usrnm", "password": "passwd"}
    :return: A dict object containing "success" and "reason" (in case of error) fields
    """
    # todo: add hashing function
    username = request.form["username"]
    user_password = request.form["password"]
    password = get_user(username)

    if not password:
        return {
            "success": False,
            "reason": "Invalid parameter provided."
        }

    if user_password != password:
        return {
            "success": False,
            "reason": "Invalid parameter provided."
        }

    session["username"] = username
    return {
        "success": True,
    }

@app.post("/signup")
def signup() -> dict:
    """
    {"username": "usrnm", "password": "passwd"}
    :return: A dict object containing "success" and "reason" (in case of error) fields
    """
    # todo: add hashing function
    username = request.form["username"]
    user_password = request.form["password"]
    password = get_user(username)

    if password:
        return {
            "success": False,
            "reason": "Invalid parameter provided."
        }

    add_user(username, password)

    session["username"] = username
    return {
        "success": True,
    }

@app.post("/logoff")
def logoff() -> dict:
    session["2"]

app.config.from_mapping(
    DATABASE="./main_db.sqlite",
    SECRET_KEY='dev',
)

app.root_path = app.root_path + "\\.."
if __name__ == "__main__":
    waitress.serve(app, host="0.0.0.0", port="8000")
