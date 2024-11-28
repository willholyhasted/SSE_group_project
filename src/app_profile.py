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


profile_bp = Blueprint('profile', __name__)