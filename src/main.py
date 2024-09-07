from os.path import join as join_path

import waitress
from flask import Flask, request, session

from db import get_user, add_user



app = Flask(__name__)


@app.route("/")
def hello_world() -> str:
    return "<p>Hello, World!</p><a href=/link>A linky link!</a>"


@app.post("/login")
def login() -> dict:
    """
    {"username", "password"}
    :return:
    """
    # todo: add hashing function
    username = request.form["username"]
    user_password = request.form["password"]
    password = get_user(username)

    if not password or user_password != password:
        return {
            "success": False,
            "reason": "Invalid parameter provided."
        }
    session["username"] = username
    return {
        "success": True,
        "reason": ""
    }


@app.post("/signup")
def signup() -> dict:
    """
    {"username", "password"}
    :return:
    """
    username = request.form["username"]
    password = request.form["password"]
    users = get_user(username)
    if users is not None:
        return {
            "success": False,
            "reason": "User with given username already exists"
        }
    add_user(username, password)
    success = get_user(username) == password
    return {
        "success": success,
        "reason": ""
    }


app.config.from_mapping(
    DATABASE="./main_db.sqlite",
    SECRET_KEY='dev',
)

app.root_path = join_path(app.root_path, "..")
if __name__ == "__main__":
    waitress.serve(app, host="0.0.0.0", port="8000")
