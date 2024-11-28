import configparser
import polars as pl
import pandas
import adbc_driver_postgresql.dbapi
from string import Template
from pathlib import Path
import os

home = Path.home() #Not sure what this does

#read in configuration file parameters from secret.ini and user_info.ini
s_config = configparser.ConfigParser()
s_config.read('database/secret.ini')
ui_config = configparser.ConfigParser()
ui_config.read('database/user_info.ini')

data_analysis_db_url = s_config['source']['data_analysis_db_url']
ui_conn = adbc_driver_postgresql.dbapi.connect(data_analysis_db_url)
ui_cur = ui_conn.cursor()

#ui_cur.execute(ui_config['query']['delete_user_info'])

ui_cur.execute(ui_config['query']['create_user_info'])

ui_conn.commit()
ui_cur.close()
ui_conn.close()

