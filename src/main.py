import flask
import waitress

app = flask.Flask(__name__)


@app.route("/")
def hello_world() -> str:
    return "<p>Hello, World!</p><a href=/link>A linky link!</a>"

@app.route("/link")
def link() -> str:
    return "<a href=\"/\">Such a clicky link!</a>"

if __name__ == "__main__":
    waitress.serve(app, host="0.0.0.0", port="8000")
