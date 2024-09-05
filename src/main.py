from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p><a href=/link>A linky link!</a>"

@app.route("/link")
def link():
    return "<a href=\"\/\">Such a clicky link!</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
