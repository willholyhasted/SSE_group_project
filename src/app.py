

from flask import Flask, render_template, request
app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods = ["POST"])
def login_submit():
    input_username = request.form.get("username")
    input_password = request.form.get("password")
    return render_template("main.html")
