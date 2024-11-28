
import configparser

def load_db_config():
    config = configparser.ConfigParser()
    config.read('database/secret.ini')
    return config["source"]["data_analysis_db_url"]