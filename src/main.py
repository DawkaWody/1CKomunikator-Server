from os.path import join as join_path

import waitress
from flask import Flask, request, session

from db import get_password, add_user, get_db
from utils import root
import timeit

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
    password = get_password(username)

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
    users = get_password(username)
    if users is not None:
        return {
            "success": False,
            "reason": "User with given username already exists"
        }
    add_user(username, password)
    success = get_password(username) == password
    return {
        "success": success,
        "reason": ""
    }

import typing

@app.route("/test")
def which_faster() -> str:
    #parsed_query_params: dict[str, str] = { (data := i.split('='))[0]: data[1] for i in request.url.split('?')[1].split('&') }
    query_params: list[str] = request.url.split('?')[1].split('&')

    username, password = query_params[0].split('=')[1], query_params[1].split('=')[1]

    if not get_password(username) is None:
        return str("Fail")

    add_user(username, password)

    tm: float = timeit.timeit(lambda: get_password(username) == password, number=1000)

    return str(tm / 1000)


app.config.from_mapping(
    DATABASE=root / "main_db.sqlite",
)

app.root_path = str(root)
if __name__ == "__main__":
    waitress.serve(app, host="0.0.0.0", port="8000")
