"""
Configuration parser
"""
import argparse
import yaml

parser=argparse.ArgumentParser()


def read_config():
    """ Read config from file"""
    try:
        with open('config.yaml', encoding="utf-8") as cf_file:
            config = yaml.safe_load(cf_file.read())
            return config
    except FileNotFoundError:
        exit("Configuration file not found! Aborting.")

def arg_parser():
    """
    Command line
    """
    parser.add_argument("file", help="The gpx file to process")
    parser.add_argument("-w", help="Set the rider weight (kg)", type=float)
    parser.add_argument("--no-cad", action="store_true", help="Ignore cadence")

    rider = read_config().get("actual")
    args = parser.parse_args()
    args.rider = rider
    if args.w:
        args.rider["M"] = args.w
    return args
