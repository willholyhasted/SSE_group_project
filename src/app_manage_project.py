import polars as pl
import configparser
import pandas
import adbc_driver_postgresql.dbapi
from string import Template
from pathlib import Path
import os
from flask import Flask, render_template, request, Blueprint
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
    project_id = project_id_info["project_id"][0]
    project_name = project_id_info["project_name"][0]

    
    applications_df = pl.read_database(
        ui_config['query']['info_for_manage_project'], connection= ui_conn)

    
    # project_id, first_name, second_name, course, enrolling_year, email, status  
    project_applications_df = applications_df.filter(pl.col("project_id") == project_id)

    project_applications_dict = project_applications_df.to_dict(as_series=False)

    return render_template("manage_project.html", )

