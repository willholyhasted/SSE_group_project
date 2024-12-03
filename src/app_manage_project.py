import polars as pl
import configparser
from pathlib import Path
from flask import (
    render_template,
    request,
    Blueprint,
    session,
    redirect,
    url_for,
)
from database.connection import get_db


home = Path.home()  # Not sure what this does

# read in configuration file parameters from secret.ini and user_info.ini
ui_config = configparser.ConfigParser()
ui_config.read("database/user_info.ini")


manage_bp = Blueprint("manage", __name__)


@manage_bp.route("/manage", methods=["GET", "POST"])
def manage_project():

    username = session.get("username")

    command = f"""
        SELECT project_id, project_name
        FROM project_info
        WHERE username = '{username}'
    """

    ui_conn = get_db()

    project_id_info = pl.read_database(command, connection=ui_conn)
    project_id = project_id_info["project_id"][0]
    project_name = project_id_info["project_name"][0]

    applications_df = pl.read_database(
        ui_config["query"]["info_for_manage_project"], connection=ui_conn
    )

    print(applications_df)

    # project_id, username, first_name, second_name, course, enrolling_year, email, status
    project_applications_df = applications_df.filter(
        pl.col("project_id") == project_id
    )

    print(project_applications_df)

    project_applications_dict = project_applications_df.to_dicts()

    print(project_applications_dict)

    return render_template(
        "manage_project.html",
        project_name=project_name,
        applicants=project_applications_dict,
    )


@manage_bp.route("/update_status", methods=["POST"])
def update_status():

    print(request.form["status"])
    print(request.form)
    print(request.form["applicant_username"])

    username = request.form["applicant_username"]
    status = request.form["status"] == "true"  # Convert to boolean

    command = f"""
        UPDATE applications_info
        SET status = {status}
        WHERE applicant = '{username}'
    """

    #  Update the applicant status in the database
    ui_conn = get_db()
    ui_cur = ui_conn.cursor()
    ui_cur.execute(command)
    ui_conn.commit()
    ui_cur.close()

    return redirect(
        url_for("manage.manage_project")
    )  # Replace 'view_project' with your route
