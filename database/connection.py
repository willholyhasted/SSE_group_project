import adbc_driver_postgresql.dbapi
from flask import g
from .config import load_db_config


def get_db():
    """Get the database connection for the current request."""
    if "db" not in g:
        db_url = load_db_config()
        g.db = adbc_driver_postgresql.dbapi.connect(db_url)
    return g.db


def close_db(exception=None):
    """Close the database connection."""
    db = g.pop("db", None)
    if db is not None:
        db.close()
