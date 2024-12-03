import polars as pl
import configparser
import pandas
import adbc_driver_postgresql.dbapi
from string import Template
from pathlib import Path
import os
from flask import Flask, render_template, request, Blueprint, session, redirect, url_for
import bcrypt
from database.connection import get_db


search_bp = Blueprint("search", __name__)


@search_bp.route("/search", methods=["POST", "GET"])
def search_project():

    username = session.get("username")

    command = f"""
            SELECT project_info.project_id, project_name, description, field1, field2, field3, application_info.applicant, status
            FROM project_info LEFT JOIN (
                SELECT project_id, applicant, status 
                FROM applications_info
                WHERE applicant = '{username}') AS application_info
            ON project_info.project_id = application_info.project_id            
            ORDER BY project_info.project_name
        """

    command_2 = f"""
                SELECT project_id, applicant, status
                FROM applications_info
                WHERE applicant = '{username}'
            """

    ui_conn = get_db()

    projects_df = pl.read_database(command, connection=ui_conn)

    projects_df = projects_df.with_columns(
        pl.concat_str(["field1", "field2", "field3"], separator=", ").alias("fields")
    )

    projects_df = projects_df.with_columns(
        pl.col("fields")
        .str.strip_chars(", ")
        .alias("fields")  # Remove trailing comma and space
    )

    projects_df = projects_df.with_columns(
        pl.col("fields")
        .str.strip_chars(", ")
        .alias("fields")  # Remove trailing comma and space
    )

    print(projects_df)

    projects_dict = projects_df.to_dicts()

    return render_template("search_page_new.html", projects=projects_dict)


@search_bp.route("/apply_project", methods=["POST", "GET"])
def apply_project():

    username = session.get("username")
    project_id = request.form["project_id"]

    command = f"""
            INSERT INTO applications_info
            (project_id, applicant, status, application_time)
            VALUES ({project_id}, '{username}', NULL, CURRENT_TIMESTAMP)
        """

    #  Update the applicant status in the database
    ui_conn = get_db()
    ui_cur = ui_conn.cursor()
    ui_cur.execute(command)
    ui_conn.commit()
    ui_cur.close()

    # we want to write to database adding an application
    # then the button should turn grey if already applied
    return redirect(url_for("search.search_project"))


@search_bp.route("/project_details", methods=["POST", "GET"])
def project_details():

    if request.method == "POST":
        project_id = request.form["project_id"]
    else:
        project_id = request.args.get("project_id")

    # now get data from the database including project id

    command = f"""
                    SELECT project_id, project_info.username, first_name, second_name, project_name, description, people, field1, field2, field3, project_info.email
                    FROM project_info LEFT JOIN user_info 
                    ON project_info.username = user_info.username
                    WHERE project_id = '{project_id}'
               """

    ui_conn = get_db()
    projects_df = pl.read_database(command, connection=ui_conn)

    pl.Config.set_tbl_cols(50)

    print(projects_df)

    projects_df = projects_df.with_columns(
        pl.concat_str(["field1", "field2", "field3"], separator=", ").alias("fields")
    )

    projects_df = projects_df.with_columns(
        pl.col("fields")
        .str.strip_chars(", ")
        .alias("fields")  # Remove trailing comma and space
    )

    projects_df = projects_df.with_columns(
        pl.col("fields")
        .str.strip_chars(", ")
        .alias("fields")  # Remove trailing comma and space
    )

    print(projects_df)

    projects_dict = projects_df.to_dicts()

    print(projects_dict)

    return render_template("project_infopage.html", projects=projects_dict)
