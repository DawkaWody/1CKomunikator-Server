"""Main module."""
import flask
from flask import render_template
import waitress

from db import DbManager
from utils import root

app = flask.Flask(__name__)


@app.route("/")
def hello_world() -> str:
    """Hello World."""
    return render_template("index.html")


@app.post("/login")
def login() -> dict:
    """Loging in.

    format is:
    {"username":<username>, "password":<password>}
    :return:
    """
    username = flask.request.form["username"]
    user_password = flask.request.form["password"]
    password = db.get_password(username)

    if not password or user_password != password:
        return {"success": False, "reason": "Invalid parameter provided."}
    flask.session["username"] = username
    return {"success": True, "reason": ""}


@app.post("/signup")
def signup() -> dict:
    """Signing up.

    format is:
    {"username":<username>, "password":<password>}
    :return:
    """
    username = flask.request.form["username"]
    password = flask.request.form["password"]
    users = db.get_password(username)
    if users is not None:
        return {"success": False, "reason": "User with given username already exists"}
    db.add_user(username, password)
    success = db.get_password(username) == password
    return {"success": success, "reason": ""}


app.config.db_path = root / "main_db.sqlite"
db = DbManager(app.config.db_path)
app.root_path = str(root)
if __name__ == "__main__":
    waitress.serve(app, host="localhost", port="8000")
