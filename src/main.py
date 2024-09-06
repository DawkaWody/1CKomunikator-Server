from enum import Enum

import waitress
from flask import Flask, request, session


class LoginErrorReason(Enum):
    invalid_username = 0,
    invalid_password = 1,
    other = 2


class AccountCreationErrorReason(Enum):
    invalid_password = 0,
    user_already_exists = 1
    other = 2


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
    input_password = request.form["password"]
    # password = get_user(username)
    password = ["admin"]  # tmp
    # if not verify_password(input_password, password):
    #    return {
    #        "success": False,
    #        "reason": LoginErrorReason.invalid_password
    #    }
    # else:
    return {
        "success": True,
    }

app.config.from_mapping(
    DATABASE="./main_db.sqlite",
    SECRET_KEY='dev',
)

app.root_path = app.root_path + "\\.."
if __name__ == "__main__":
    waitress.serve(app, host="0.0.0.0", port="8000")
