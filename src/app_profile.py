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



app = Flask(__name__)
profile_bp = Blueprint('profile', __name__)

@app.route('/profile/<username>')
def profile(username):
    # SQL command to get the user information
    command = f"""
    SELECT Name, Course, Enrolling_Year, Email, GitHub_URL, LinkedIn_URL
    FROM user_info
    WHERE username = '{username}'
    """
    
    # Connect to the database
    ui_conn = get_db()
    
    # Execute SQL command and fetch data
    user_info = pl.read_database(command, connection=ui_conn)
    
    # Check if user exists in the database
    if len(user_info) == 0:
        return "User not found", 404
    
    # Extract user data from the DataFrame
    name = user_info[0, "Name"]
    course = user_info[0, "Course"]
    enrolling_year = user_info[0, "Enrolling_Year"]
    email = user_info[0, "Email"]
    github_url = user_info[0, "GitHub_URL"]
    linkedin_url = user_info[0, "LinkedIn_URL"]
    
    # Render the HTML page using data from the database
    return render_template(
        'profile.html',
        name=name,
        course=course,
        enrolling_year=enrolling_year,
        email=email,
        github_url=github_url,
        linkedin_url=linkedin_url
    )

if __name__ == '__main__':
    app.run(debug=True)
