"""
Configuration parser
"""
import yaml


def read_config():
    """ Read config from file"""
    try:
        with open('config.yaml', encoding="utf-8") as cf_file:
            config = yaml.safe_load(cf_file.read())
            return config
    except FileNotFoundError:
        print("Configuration file not found! Aborting.")
