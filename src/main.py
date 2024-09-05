from flask import Flask
import base64

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p><a href=/link>A linky link!</a>"

@app.route("/link")
def link():
    return f"<a href=\"{base64.urlsafe_b64decode(base64.urlsafe_b64decode(base64.urlsafe_b64decode(b'WVVoU01HTklUVFpNZVRsM1lrTTFkMkl6U25WaFNGWnBURzFPZG1KVE9EMD0='))).decode(encoding="utf-8")}\">Such a clicky link!</a>"

app.run("localhost", 2000)