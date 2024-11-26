import polars
import configparser
import pandas
import adbc_driver_postgresql.dbapi
from string import Template
from pathlib import Path
import os
from flask import Flask, render_template, request
import bcrypt
app = Flask(__name__)

#read in configuration file parameters from secret.ini and user_info.ini
s_config = configparser.ConfigParser()
s_config.read('database/secret.ini')
ui_config = configparser.ConfigParser()
ui_config.read('database/user_info.ini')

data_analysis_db_url = s_config['source']['data_analysis_db_url']
ui_conn = adbc_driver_postgresql.dbapi.connect(data_analysis_db_url)
ui_cur = ui_conn.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods = ["POST"])
def login():
    input_username = request.form.get("username")
    input_password = request.form.get("password")

    command = f"""
    SELECT username, password
    FROM user_info
    WHERE username = {input_username}
    """

    user_info = polars.read_database(command, connection= ui_conn)

    #salt = bcrypt.gensalt() #this creates a 60 character hash
    #hash_pswd = bcrypt.hashpw(input_password.encode(), salt)

    hashed_password = user_info[0,"password"]
    if bcrypt.checkpw(input_password.encode(), hashed_password):
        return render_template("main.html")
    else:
        return render_template("index.html")



def login_test():
    input_username = "danny"
    input_password = "hello"

    command = f"""
    SELECT username, password
    FROM user_info
    WHERE username = '{input_username}'
    """

    user_info = polars.read_database(command, connection= ui_conn)

    print(user_info)

    return

if __name__ == "__main__":
    login_test()