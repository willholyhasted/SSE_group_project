import polars as pl
import configparser
import pandas
import adbc_driver_postgresql.dbapi
from string import Template
from pathlib import Path
import os
from flask import Flask, render_template, request, Blueprint, session
import bcrypt
from database.connection import get_db


create_bp = Blueprint('create', __name__)


@create_bp.route("/create", methods = ["POST"])
def create_project():
    return render_template("project_page.html")

#@login_bp.route("/login", methods = ["POST"])

@create_bp.route("/project", methods = ["POST"])
def submit_project():
    project_name = request.form.get("project-name")
    username =  session.get('username')
    description = request.form.get("description")
    people = int(request.form.get("people"))
    field = request.form.getlist("field")

    if len(field) == 1:
        field1 = field[0]
        field2 = ""
        field3 = ""
    elif len(field) == 2:
        field1 = field[0]
        field2 = field[1]
        field3 = ""
    else:
        field1 = field[0]
        field2 = field[1]
        field3 = field[2]

    email = request.form.get("email")

    project_data_df = pl.DataFrame({

        "project_name": [project_name],
        "username": [username],
        "description": [description],
        "people": [people],
        "field1": [field1],
        "field2": [field2],
        "field3": [field3],
        "email": [email]
    })

    existing_project_query = f"""
    SELECT COUNT(*) AS count
    FROM project_info
    WHERE project_name = '{project_name}'
    """
    ui_conn = get_db()
    existing_project = pl.read_database(existing_project_query, connection= ui_conn)
    if existing_project[0, "count"] > 0:
        return render_template("project_page.html", error="Project name already exists.")

    #pl.Config.set_tbl_cols(50) #for debugging
    #print(project_data_df)     #for debugging

    try:
        ui_conn = get_db()

        project_data_df.write_database(
            table_name='project_info',
            if_table_exists='append',
            connection=ui_conn
        )

        return render_template("main.html")

    except Exception as e:
        return render_template("project_page.html", error=f"An error occurred: {e}")

