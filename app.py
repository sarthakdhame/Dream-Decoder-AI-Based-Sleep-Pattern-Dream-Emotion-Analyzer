from flask import Flask
import os

app = Flask(__name__, static_folder="frontend", static_url_path="")


@app.route("/")
def serve_index():
    return app.send_static_file("index.html")
