import os
import configparser


def load_db_config():
    """Load the database configuration based on the environment."""
    if os.getenv("FLASK_ENV") == "production":
        # In production, read from the environment variable
        db_url = os.getenv("DATA_ANALYSIS_DB_URL")
        if not db_url:
            raise RuntimeError("Database URL not set in the environment.")
        return db_url
    else:
        # In local, read from the secret.ini file
        config = configparser.ConfigParser()
        config.read("database/secret.ini")
        if (
            "source" not in config
            or "data_analysis_db_url" not in config["source"]
        ):
            raise RuntimeError("Database URL not found in secret.ini.")
        return config["source"]["data_analysis_db_url"]
