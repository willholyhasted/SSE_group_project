

from flask import Flask, render_template, request
app = Flask(__name__)
@app.route("/")
def hello_world():
    return "Hello World!"

"""
#This code is for when front-end team are finished
@app.route("/")
def hello_world():
    return render_template("index.html")
"""

