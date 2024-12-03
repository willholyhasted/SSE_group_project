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
from flask import session
import requests
import base64
from datetime import datetime


profile_bp = Blueprint('profile', __name__)





@profile_bp.route('/profile/', defaults={'username': None}, methods = ["POST"])
@profile_bp.route("/profile/<string:username>", methods = ["POST"])
def create_view(username):
    # SQL command to get the user information
    if username is None:
        input_username = session.get('username')  # Store the username in the session
    else:
        input_username = username

    command = f"""
    SELECT first_name, second_name, course, enrolling_year, email, github, linkedin, bio
    FROM user_info
    WHERE username = '{input_username}'
    """

    # Connect to the database
    ui_conn = get_db()

    # Execute SQL command and fetch data
    user_info = pl.read_database(command, connection=ui_conn)

    # Check if user exists in the database
    if len(user_info) == 0:
        return "User not found", 404

    
    # Extract user data from the DataFrame
    first_name = user_info["first_name"][0]
    second_name = user_info["second_name"][0]
    course = user_info["course"][0]
    enrolling_year = user_info["enrolling_year"][0]
    email = user_info["email"][0]
    github_url = user_info["github"][0]
    linkedin_url = user_info["linkedin"][0]
    bio = user_info["bio"][0]
    

    # Get the api
    input_name = github_url.split('/')[3]
    response = requests.get(f"https://api.github.com/users/{input_name}/repos")
    REPOS = []
    if response.status_code == 200:
        repos = response.json()
    else:
        repos = []
        print(f"Error: {response.status_code}")
    for repo in repos:
        full_name = repo['full_name']
        repo_name = full_name.split('/')[1]
        time = repo['updated_at']
        time_obj = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")

        # Format the datetime object into the desired string
        formatted_time = time_obj.strftime("%d %B %Y, %H:%M")
        response_repo = requests.get(
            f"https://api.github.com/repos/{full_name}")
        star = response_repo.json()['stargazers_count']
        response_language = requests.get(
            f"https://api.github.com/repos/{full_name}/languages")
        languages = response_language.json()
        languages_names = list(languages.keys())
        response_readme = requests.get(
             f"https://api.github.com/repos/{full_name}/readme")
        readme = response_readme.json().get("content", "")
        readmetext = base64.b64decode(readme).decode('utf-8')
        
        REPOS.append(
            {'repo': repo_name,
             'time': formatted_time,
             'star': star,
             'languages': languages_names,
             'readme': readmetext})

    return render_template("profileTest.html", first_name=first_name, second_name=second_name, course=course, 
                           enrolling_year=enrolling_year, email=email, github_url=github_url,linkedin_url=linkedin_url, bio=bio, repos=REPOS)

