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


home = Path.home() #Not sure what this does

#read in configuration file parameters from secret.ini and user_info.ini
ui_config = configparser.ConfigParser()
ui_config.read('database/user_info.ini')


manage_bp = Blueprint('manage', __name__)

@manage_bp.route("/manage", methods = ["POST"])
def manage_project():

    username =  session.get('username')

    command = f"""
        SELECT project_id, project_name
        FROM project_info
        WHERE username = '{username}'
    """

    ui_conn = get_db()

    project_id_info = pl.read_database(command, connection= ui_conn)

    print(project_id_info)

    project_id = project_id_info["project_id"][0]
    project_name = project_id_info["project_name"][0]


    print(f"project_id: {project_id}")
    print(f"project_name: {project_name}")

    
    applications_df = pl.read_database(
        ui_config['query']['info_for_manage_project'], connection= ui_conn)


    print(applications_df)

    
    # project_id, first_name, second_name, course, enrolling_year, email, status  
    project_applications_df = applications_df.filter(pl.col("project_id") == project_id)

    print(project_applications_df)

    project_applications_dict = project_applications_df.to_dicts()

    print(project_applications_dict)

    return render_template("manage_project.html", project_name = project_name, applicants=project_applications_dict)

