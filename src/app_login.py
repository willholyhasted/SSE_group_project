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


login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["POST"])
def login():
    input_username = request.form.get("username")
    input_password = request.form.get("password")

    session["username"] = input_username  # Store the username in the session

    command = f"""
    SELECT username, password
    FROM user_info
    WHERE username = '{input_username}'
    """
    ui_conn = get_db()

    user_info = pl.read_database(command, connection=ui_conn)

    if user_info.is_empty():  # Handle case where username doesn't exist
        return render_template("index.html", error="Username does not exist.")

    hashed_password_db = user_info[0, "password"]
    hashed_password_db_bytes = hashed_password_db.encode()

    if bcrypt.checkpw(input_password.encode(), hashed_password_db_bytes):
        return redirect(url_for("login.main"))
    else:
        return render_template(
            "index.html", error="Username and password do not match."
        )


@login_bp.route("/main", methods=["GET", "POST"])
def main():

    username = session.get("username")

    events = fetch_events()

    project = f"""
            SELECT project_id
            FROM project_info
            WHERE username = '{username}'
            """
    ui_conn = get_db()
    existing_project = pl.read_database(project, connection=ui_conn)

    if len(existing_project) > 0:
        return render_template(
            "main.html",
            project_id=existing_project[0, "project_id"],
            events=events,
            Has_project=True,
        )
    else:
        return render_template(
            "main.html", project_id="", events=events, Has_project=False
        )


@login_bp.route("/register")
def register():
    return render_template("register_page.html")


@login_bp.route("/registerSubmit", methods=["POST"])
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
    bio = request.form.get("bio")

    existing_user_query = f"""
    SELECT COUNT(*) AS count
    FROM user_info
    WHERE username = '{username}'
    """
    ui_conn = get_db()
    existing_user = pl.read_database(existing_user_query, connection=ui_conn)
    if existing_user[0, "count"] > 0:
        return render_template(
            "register_page.html", error="Username already exists."
        )

    salt = bcrypt.gensalt()  # this creates a 60 character hash
    hashed_password = bcrypt.hashpw(input_password.encode(), salt)

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

    # pl.Config.set_tbl_cols(50)
    # print(user_data_df)

    try:

        ui_conn = get_db()

        user_data_df.write_database(
            table_name="user_info",
            if_table_exists="append",
            connection=ui_conn,
        )

        return render_template("index.html")

    except Exception as e:
        return render_template(
            "register_page.html", error=f"An error occurred: {e}"
        )
