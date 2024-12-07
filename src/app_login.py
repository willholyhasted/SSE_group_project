import polars as pl
from flask import (
    render_template,
    request,
    Blueprint,
    session,
    redirect,
    url_for,
)
import bcrypt
from database.connection import get_db
from .api import fetch_events

# *************  DESCRIPTION: ********************************
# This page handles requests from the user to login or register a new account
# It checks if their username and password are stored in the user_info table
# If the user does not have an account, it provides the option to create one
# *************************************************************

# Create a Flask Blueprint named "login" for the login page
login_bp = Blueprint("login", __name__)


# Define a route for user login
@login_bp.route("/login", methods=["POST"])
def login():
    # Retrieve the username and password from the form submission
    input_username = request.form.get("username")
    input_password = request.form.get("password")

    # Store the username in the session for later use
    session["username"] = input_username

    # SQL query to fetch the user's username and hashed password from the database
    command = f"""
    SELECT username, password
    FROM user_info
    WHERE username = '{input_username}'
    """

    # Get a database connection
    ui_conn = get_db()

    # Execute the query and store the result in a Polars DataFrame
    user_info = pl.read_database(command, connection=ui_conn)

    # Check if the username exists in the database
    if user_info.is_empty():
        # If the username doesn't exist, render the login page with an error message
        return render_template("index.html", error="Username does not exist.")

    # Extract the hashed password from the database
    hashed_password_db = user_info[0, "password"]
    hashed_password_db_bytes = hashed_password_db.encode()

    # Verify the input password against the hashed password using bcrypt
    if bcrypt.checkpw(input_password.encode(), hashed_password_db_bytes):
        # Redirect to the main page if authentication is successful
        return redirect(url_for("login.main"))
    else:
        # Render the login page with an error message if authentication fails
        return render_template(
            "index.html", error="Username and password do not match."
        )


# Define a route for the main page that accepts both GET and POST requests
@login_bp.route("/main", methods=["GET", "POST"])
def main():

    # Retrieve the username from the session
    username = session.get("username")

    events = fetch_events()

    # Query to check if the user has an existing project
    project = f"""
            SELECT project_id
            FROM project_info
            WHERE username = '{username}'
            """
    # Connect to the database
    ui_conn = get_db()

    # Execute the SQL query defined above
    existing_project = pl.read_database(project, connection=ui_conn)

    # Check if the user has a project
    if len(existing_project) > 0:
        # Render the main page with the project ID and events if a project exists
        return render_template(
            "main.html",
            project_id=existing_project[0, "project_id"],
            events=events,
            Has_project=True,
        )
    else:
        # Render the main page, passing the information that the user does not have a project associated
        return render_template(
            "main.html", project_id="", events=events, Has_project=False
        )


# Define a route for rendering the registration page
@login_bp.route("/register")
def register():
    # Render the registration page template
    return render_template("register_page.html")


# Define a route to handle registration form submissions for a new user
@login_bp.route("/registerSubmit", methods=["POST"])
def register_submit():
    # Retrieve user input from the registration form
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
    bio = request.form.get("bio")

    # Query to check if the username already exists in the database
    existing_user_query = f"""
    SELECT COUNT(*) AS count
    FROM user_info
    WHERE username = '{username}'
    """

    # Get a database connection
    ui_conn = get_db()
    existing_user = pl.read_database(existing_user_query, connection=ui_conn)

    # If the username already exists, render the registration page with an error message
    if existing_user[0, "count"] > 0:
        return render_template(
            "register_page.html", error="Username already exists."
        )

    # Generate a salt for password hashing
    salt = bcrypt.gensalt()
    # Hash the user's password with the salt (60 character hash)
    hashed_password = bcrypt.hashpw(input_password.encode(), salt)

    # Create a Polars DataFrame with the user's registration data
    user_data_df = pl.DataFrame(
        {
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
            "bio": [bio],
        }
    )

    try:
        # Insert the user data into the "user_info" table
        user_data_df.write_database(
            table_name="user_info",
            if_table_exists="append",
            connection=ui_conn,
        )

        # Render the login page after successful registration
        return render_template("index.html")

    except Exception as e:
        # If an error occurs, render the registration page with an error message
        return render_template(
            "register_page.html", error=f"An error occurred: {e}"
        )
