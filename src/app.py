import polars as pl
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
    WHERE username = '{input_username}'
    """

    user_info = pl.read_database(command, connection= ui_conn)

    hashed_password_db = user_info[0,"password"]

    hashed_password_db_bytes = hashed_password_db.encode()

    if bcrypt.checkpw(input_password.encode(), hashed_password_db_bytes):
        return render_template("main.html")
    else:
        return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register_page.html")


@app.route("/registerSubmit", methods = ["POST"])
def register_submit():
    first_name = request.form.get("first-name")
    second_name = request.form.get("last-name")
    username = request.form.get("username")
    input_password = request.form.get("password")
    degree = request.form.get("degree")
    course = request.form.get("course")
    start = int(request.form.get("enrolling-year"))
    github = request.form.get("github")
    linkedin = request.form.get("linkedin")
    email = request.form.get("email")
    bio =request.form.get("bio")

    salt = bcrypt.gensalt() #this creates a 60 character hash
    hashed_password = bcrypt.hashpw(input_password.encode(), salt)

    user_data_df = pl.DataFrame({

        "username": [username],
        "password": [hashed_password],  # Store the hashed password
        "first_name": [first_name],
        "second_name": [second_name],
        "course": [course],
        "degree_type": [degree],
        "enrolling_year": [start],
        "email": [email],
        "github": [github],
        "linkedin": [linkedin],
        "bio": [bio]
    })

    pl.Config.set_tbl_cols(50)
    print(user_data_df)

    try:

        user_data_df.write_database(
            table_name='user_info',
            if_table_exists='append',
            connection=ui_conn
        )

        return render_template("index.html")

    except Exception as e:
        return render_template("register.html", error = f"An error occurred: {e}")


@app.route("/register")
def register():
    return render_template("register_page.html")

@app.route("/project") #function that will inject data to database
def register():
    return render_template("register_page.html")


if __name__ == "__main__":
    app.run(debug=True)