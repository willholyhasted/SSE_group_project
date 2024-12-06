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
# This page handles requests from the user to create a new project
# Each user can create at most one project
# It interacts with the project_info table which stores data at the project level
# *************************************************************

# Create a Flask Blueprint named "create" for the creation of a new project
create_bp = Blueprint("create", __name__)


# Define a route for rendering the project creation page
@create_bp.route("/create", methods=["POST"])
def create_project():
    return render_template("project_page.html")


# Define a route for submitting a new project's data
@create_bp.route("/project", methods=["POST"])
def submit_project():
    # Save the inputs as separate variables from the html project_page.html
    project_name = request.form.get("project-name")
    username = session.get("username")
    description = request.form.get("description")
    people = int(request.form.get("people"))
    field = request.form.getlist("field")
    email = request.form.get("email")

    # Depending on how many "fields" a project is associated with (max 3), save any empty fields as an empty string
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

    # Save the variables to a polars data frame
    project_data_df = pl.DataFrame(
        {
            "project_name": [project_name],
            "username": [username],
            "description": [description],
            "people": [people],
            "field1": [field1],
            "field2": [field2],
            "field3": [field3],
            "email": [email],
        }
    )

    # Check if project_name already exists - if so return an error
    existing_project_query = f"""
    SELECT COUNT(*) AS count
    FROM project_info
    WHERE project_name = '{project_name}'
    """

    # Connect to the supabase database
    ui_conn = get_db()

    # Call the SQL code defined above, with the connection ui_conn
    existing_project = pl.read_database(
        existing_project_query, connection=ui_conn
    )

    # if the project exists already, return an error
    if existing_project[0, "count"] > 0:
        return render_template(
            "project_page.html", error="Project name already exists."
        )

    # pl.Config.set_tbl_cols(50) #for debugging
    # print(project_data_df)     #for debugging

    try:
        # Write the new project details to the project_info table
        project_data_df.write_database(
            table_name="project_info",
            if_table_exists="append",
            connection=ui_conn,
        )

        # Go back to login page
        return redirect(url_for("login.main"))

    except Exception as e:
        return render_template(
            "project_page.html", error=f"An error occurred: {e}"
        )
