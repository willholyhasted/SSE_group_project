import polars as pl
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
# This page allows a user to find a list of projects to apply for
# It connects to the project_info table and applications_info table
# The user can directly apply for a project, and see the status of previous applications
# *************************************************************


# Create a Flask Blueprint for the project search module
search_bp = Blueprint("search", __name__)

# Define a route for searching and listing projects
@search_bp.route("/search", methods=["POST", "GET"])
def search_project():

    # Get the logged-in username from the session
    username = session.get("username")

    # SQL query to fetch project information, including application status if the user has applied
    # This query left joins a filtered version of the applications_info table on the project_info table
    command = f"""
            SELECT project_info.project_id, project_name, description, field1, field2, field3, application_info.applicant, status
            FROM project_info LEFT JOIN (
                SELECT project_id, applicant, status 
                FROM applications_info
                WHERE applicant = '{username}') AS application_info
            ON project_info.project_id = application_info.project_id            
            ORDER BY project_info.project_name
        """

    # Establish a connection to the database
    ui_conn = get_db()

    # Execute the above query and store the result as a polars DataFrame
    projects_df = pl.read_database(command, connection=ui_conn)

    # Combine field1, field2, and field3 into a single "fields" column with a comma-separated list
    projects_df = projects_df.with_columns(
        pl.concat_str(["field1", "field2", "field3"], separator=", ").alias(
            "fields"
        )
    )

    # Clean up the "fields" column by removing any trailing commas (in case only 2 out 3 fields non-null)
    projects_df = projects_df.with_columns(
        pl.col("fields")
        .str.strip_chars(", ")
        .alias("fields")  # Remove trailing comma and space
    )

    # Do this again (in case only 1 out 3 fields non-null)
    projects_df = projects_df.with_columns(
        pl.col("fields")
        .str.strip_chars(", ")
        .alias("fields")  # Remove trailing comma and space
    )

    # Convert to a list of dictionaries in order to pass to html
    projects_dict = projects_df.to_dicts()

    # Render the "search_page_new.html" template, passing the projects data
    return render_template("search_page_new.html", projects=projects_dict)


# Define a route for applying to a project
@search_bp.route("/apply_project", methods=["POST", "GET"])
def apply_project():

    # Get the logged-in username and the project ID from the form data
    username = session.get("username")
    project_id = request.form["project_id"]

    # SQL query to insert a new application into the applications_info table
    command = f"""
            INSERT INTO applications_info
            (project_id, applicant, status, application_time)
            VALUES ({project_id}, '{username}', NULL, CURRENT_TIMESTAMP)
        """

    # Execute the query to add the application to the database
    ui_conn = get_db()
    ui_cur = ui_conn.cursor()
    ui_cur.execute(command)
    ui_conn.commit()
    ui_cur.close()

    # Redirect the user back to the project search page after applying
    return redirect(url_for("search.search_project"))


# Define a route for viewing detailed information about a specific project
@search_bp.route("/project_details", methods=["POST", "GET"])
def project_details():

    # Get the project ID from the form data (POST) or query string (GET)
    if request.method == "POST":
        project_id = request.form["project_id"]
    else:
        project_id = request.args.get("project_id")

    # SQL query to fetch detailed information about the selected project
    command = f"""
                    SELECT project_id, project_info.username, first_name, second_name, project_name, description, people, field1, field2, field3, project_info.email
                    FROM project_info LEFT JOIN user_info 
                    ON project_info.username = user_info.username
                    WHERE project_id = '{project_id}'
               """

    # Establish a connection to the database
    ui_conn = get_db()
    projects_df = pl.read_database(command, connection=ui_conn)

    # Combine field1, field2, and field3 into a single "fields" column with a comma-separated list
    projects_df = projects_df.with_columns(
        pl.concat_str(["field1", "field2", "field3"], separator=", ").alias(
            "fields"
        )
    )

    # Clean up the "fields" column by removing any trailing commas (in case only 2 out 3 fields non-null)
    projects_df = projects_df.with_columns(
        pl.col("fields")
        .str.strip_chars(", ")
        .alias("fields")  # Remove trailing comma and space
    )

    # Do this again (in case only 1 out 3 fields non-null)
    projects_df = projects_df.with_columns(
        pl.col("fields")
        .str.strip_chars(", ")
        .alias("fields")  # Remove trailing comma and space
    )

    # Convert to a list of dictionaries to pass to html
    projects_dict = projects_df.to_dicts()

    # Render the "project_infopage.html" template, passing the project details
    return render_template("project_infopage.html", projects=projects_dict)
