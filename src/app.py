from flask import Flask, render_template
from .app_login import login_bp
from .app_create_project import create_bp
from .app_manage_project import manage_bp
from .app_profile import profile_bp
from .app_search_project import search_bp
from database.connection import close_db

# Create an instance of the Flask class for the web application
app = Flask(__name__)

# Register blueprints to modularize the application
# Each blueprint corresponds to a specific set of routes and functionality
app.register_blueprint(login_bp)
app.register_blueprint(create_bp)
app.register_blueprint(manage_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(search_bp)

#  Set the secret key for the application
#  Required for session handling
app.secret_key = "your_secret_key"


# Function to clean up database connections
@app.teardown_appcontext
def cleanup(expection=None):
    # Call the close_db function to close the database connection
    close_db(expection)


# Define a route for the home page ("/")
@app.route("/")
def index():
    # Render and return the "index.html" template when the home page is accessed
    return render_template("index.html")


# if __name__ == "__main__":
# app.run(debug=True)
# port = int(os.getenv("PORT", 5000))  # Default to 5000 if PORT is not set
# app.run(host="0.0.0.0", port=port)
