import waitress
import flask

from db import get_password, add_user, get_db, load_script_templates
from utils import root

app = flask.Flask(__name__)

load_script_templates()

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
    username = flask.request.form["username"]
    user_password = flask.request.form["password"]
    password = get_password(username)

    if not password or user_password != password:
        return {
            "success": False,
            "reason": "Invalid parameter provided."
        }
    flask.session["username"] = username
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
    username = flask.request.form["username"]
    password = flask.request.form["password"]
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

app.config.from_mapping(
    DATABASE=root / "main_db.sqlite",
)

app.root_path = str(root)
if __name__ == "__main__":
    waitress.serve(app, host="0.0.0.0", port="8000")
