import polars as pl
from flask import render_template, Blueprint
from database.connection import get_db
from flask import session
import requests
import base64
from datetime import datetime
import os


# *************  DESCRIPTION: ********************************
# This page allows one to visualise their own, or applicant's, profile page
# It connects to the user_info table and displays their personal data
# It also connects to the GitHub API to display relevant information from their profile
# *************************************************************

# Create a Flask Blueprint for the profile module
profile_bp = Blueprint("profile", __name__)


# Define a route for viewing profiles
# Defaults to the logged-in user's profile if no username is provided
@profile_bp.route("/profile/", defaults={"username": None}, methods=["POST"])
@profile_bp.route("/profile/<string:username>", methods=["POST"])
def create_view(username):
    # Determine which username to query
    # If no username is specified, use the logged-in user's username from the session
    if username is None:
        input_username = session.get("username")
    else:
        input_username = username

    # SQL command to fetch the user's profile details from the user_info table
    command = f"""
    SELECT first_name, second_name, course, enrolling_year, email, github, linkedin, bio
    FROM user_info
    WHERE username = '{input_username}'
    """

    # Connect to the database
    ui_conn = get_db()

    # Execute the SQL query and store the result in a polars DataFrame
    user_info = pl.read_database(command, connection=ui_conn)

    # Handle the case where the username does not exist in the database
    if len(user_info) == 0:
        return "User not found", 404

    # Extract user data from the query result
    first_name = user_info["first_name"][0]
    second_name = user_info["second_name"][0]
    course = user_info["course"][0]
    enrolling_year = user_info["enrolling_year"][0]
    email = user_info["email"][0]
    github_url = user_info["github"][0]
    linkedin_url = user_info["linkedin"][0]
    bio = user_info["bio"][0]

    # Extract the GitHub username from the GitHub profile URL
    input_name = github_url.split("/")[3]
    # TOKEN = os.getenv("GITHUB_PAT")
    TOKEN = "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"
    headers = {"Authorization": f"token {TOKEN}"}

    # Make an API call to fetch the user's public repositories
    response = requests.get(
        f"https://api.github.com/users/{input_name}/repos", headers=headers
    )

    REPOS = []  # Initialize an empty list to store repository details

    # Check if the GitHub API request was successful
    if response.status_code == 200:
        repos = response.json()  # Parse the JSON response
    else:
        repos = []  # If the request fails, use an empty list
        print(f"Error: {response.status_code}")

    # Iterate through the list of repositories
    for repo in repos:
        full_name = repo[
            "full_name"
        ]  # Get the repository's full name (e.g., "username/repo_name")
        repo_name = full_name.split("/")[1]  # Extract the repository name
        time = repo[
            "updated_at"
        ]  # Get the last updated time of the repository
        time_obj = datetime.strptime(
            time, "%Y-%m-%dT%H:%M:%SZ"
        )  # Convert to datetime object

        # Format the datetime object into a user-friendly string
        formatted_time = time_obj.strftime("%d %B %Y, %H:%M")

        # Fetch additional repository details (e.g., star count, languages, and README)
        response_repo = requests.get(
            f"https://api.github.com/repos/{full_name}"
        )
        star = response_repo.json()["stargazers_count"]  # Get the star count
        response_language = requests.get(
            f"https://api.github.com/repos/{full_name}/languages"
        )
        languages = (
            response_language.json()
        )  # Get the programming languages used
        languages_names = list(languages.keys())  # Extract language names
        response_readme = requests.get(
            f"https://api.github.com/repos/{full_name}/readme"
        )
        readme = response_readme.json().get(
            "content", ""
        )  # Get the base64-encoded README content
        readmetext = base64.b64decode(readme).decode("utf-8")  # Decode to text

        # Add the repository details to the REPOS list
        REPOS.append(
            {
                "repo": repo_name,
                "time": formatted_time,
                "star": star,
                "languages": languages_names,
                "readme": readmetext,
            }
        )

    # Render the "profile.html" template with user details and repository information
    return render_template(
        "profile.html",
        first_name=first_name,
        second_name=second_name,
        course=course,
        enrolling_year=enrolling_year,
        email=email,
        github_url=github_url,
        linkedin_url=linkedin_url,
        bio=bio,
        repos=REPOS,
    )
