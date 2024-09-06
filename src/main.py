from flask import Flask, request
import waitress

app = Flask(__name__)


@app.route("/")
def hello_world() -> str:
    return "<p>Hello, World!</p><a href=/link>A linky link!</a>"


@app.post("/login")
def login() -> str:
    """
    {"username", "password"}
    :return:
    """
    # todo: add hsshing function p
    data: dict = request.form
    print(data["username"])
    return "Test"



app.config.from_mapping(
    DATABASE="./main_db.sqlite",
    SECRET_KEY='dev',
)

app.root_path = app.root_path + "\\.."
if __name__ == "__main__":
    waitress.serve(app, host="0.0.0.0", port="8000")
