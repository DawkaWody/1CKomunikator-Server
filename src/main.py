from flask import Flask, request, session
import waitress
from db import add_user
from enum import Enum

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
    # todo: add hashing function p
    data: dict = request.form

    session["username"] = data["username"]
    session["password"] = data["password"]

    #if not user_exists(data["username"]):
    add_user(data["username"], data["password"])
    # ^ Odrazu loguje ^
    #else:
    #get_user(data["username])
    #Sprawdzenie poprawności hasła, zalogowanie

    return { "Success": False, "reason": LoginFailureReason.invalid_password }




app.config.from_mapping(
    DATABASE="./main_db.sqlite",
    SECRET_KEY='dev',
)

app.root_path = app.root_path + "\\.."
if __name__ == "__main__":
    waitress.serve(app, host="0.0.0.0", port="8000")
