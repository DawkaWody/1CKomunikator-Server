from flask import Flask
import base64

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p><a href=/link>A linky link!</a>"

@app.route("/link")
def link():
    return "<a href=\"\\\">Such a clicky link!</a>"

app.run("localhost", 2000)