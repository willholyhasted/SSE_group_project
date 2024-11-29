import polars as pl
import configparser
import pandas
import adbc_driver_postgresql.dbapi
from string import Template
from pathlib import Path
import os
from flask import Flask, render_template, request
import bcrypt
from .app_login import login_bp
from .app_create_project import create_bp
from .app_manage_project import manage_bp
# from .app_profile import profile_bp
from .app_search_project import search_bp

from database.connection import close_db
app = Flask(__name__)
app.register_blueprint(login_bp)
app.register_blueprint(create_bp)
app.register_blueprint(manage_bp)
# app.register_blueprint(profile_bp)
app.register_blueprint(search_bp)

app.secret_key = "your_secret_key"  # Required for session handling

@app.teardown_appcontext
def cleanup(expection=None):
    close_db(expection)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/project") #function that will inject data to database
def register():
    return render_template("register_page.html")


if __name__ == "__main__":
    app.run(debug=True)