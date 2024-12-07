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

# *************  DESCRIPTION: ********************************
# This page allows a user to visualise and accept/reject applications to their project
# It subsequently connects and updates the applications_info table
# *************************************************************

# Get the user's home directory (useful for debugging)
home = Path.home()

# read in configuration file parameters from secret.ini and user_info.ini
ui_config = configparser.ConfigParser()
ui_config.read("database/user_info.ini")

# Create a Flask Blueprint for this module
manage_bp = Blueprint("manage", __name__)


# Define a route for managing project applications
@manage_bp.route("/manage", methods=["GET", "POST"])
def manage_project():

    # Get the logged-in username from the session
    username = session.get("username")

    # SQL command to fetch the user's project details (ID and name) from the database
    command = f"""
        SELECT project_id, project_name
        FROM project_info
        WHERE username = '{username}'
    """

    # Establish a database connection
    ui_conn = get_db()

    # Execute the query to get project details and save as local variables
    project_id_info = pl.read_database(command, connection=ui_conn)
    project_id = project_id_info["project_id"][0]
    project_name = project_id_info["project_name"][0]

    # SQL query on the applications_info table to fetch the usernames of all applicants for each project
    applications_df = pl.read_database(
        ui_config["query"]["info_for_manage_project"], connection=ui_conn
    )

    # We filter to find applicants to the specific project associated with the current user
    project_applications_df = applications_df.filter(
        pl.col("project_id") == project_id
    )

    # Convert to a list of dictionaries (row-wise) in order to pass to html
    project_applications_dict = project_applications_df.to_dicts()

    # Render the "manage_project.html" template with the project name and application data
    return render_template(
        "manage_project.html",
        project_name=project_name,
        applicants=project_applications_dict,
    )


# Define a route to accept or reject a project application
@manage_bp.route("/update_status", methods=["POST"])
def update_status():

    # Extract the applicant username and status from the form data
    username = request.form["applicant_username"]
    status = request.form["status"] == "true"  # Convert to boolean

    # SQL command to update the application status in the database
    command = f"""
        UPDATE applications_info
        SET status = {status}
        WHERE applicant = '{username}'
    """

    # Establish a database connection and execute the update query
    ui_conn = get_db()
    ui_cur = ui_conn.cursor()
    ui_cur.execute(command)
    ui_conn.commit()
    ui_cur.close()

    # Redirect back to the manage project page after updating the status
    return redirect(url_for("manage.manage_project"))
