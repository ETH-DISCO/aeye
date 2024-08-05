import getopt
import json
import os
import sys

from dotenv import load_dotenv

from ..CONSTANTS import *


def parsing():
    # Remove 1st argument from the list of command line arguments
    arguments = sys.argv[1:]

    # Options
    options = "hn:d:r:"

    # Long options
    long_options = ["help", "name", "directory", "resized"]

    # Prepare flags
    new_location = {"directory": "", "resized": False}

    # Parsing argument
    arguments, values = getopt.getopt(arguments, options, long_options)

    if len(arguments) > 0 and arguments[0][0] in ("-h", "--help"):
        print(f'This script populates a vector store with embeddings.\n\
        -n or --name: name of the new location.\n\
        -d or --directory: directory for new location.\n\
        -c or --resized: whether there is a directory for resized images (y/n), default is '
              f'{"n" if not new_location["resized"] else "y"}.')
        sys.exit()

    # Checking each argument
    for arg, val in arguments:
        if arg in ("-n", "--name"):
            new_location["name"] = val
        elif arg in ("-d", "--directory"):
            new_location["directory"] = val
        elif arg in ("-r", "--resized"):
            if val.lower() == "y":
                new_location["resized"] = True
            elif val.lower() == "n":
                new_location["resized"] = False
            else:
                raise ValueError("resized must be y or n.")

    return new_location


def recursive_search_of_locations(nginx_config, new_location):
    # Recursively search for the "locations" key in the nginx configuration file and add the new value to it.
    for key, value in nginx_config.items():
        if isinstance(value, dict):
            if key == "locations":
                if not new_location["resized"]:
                    value["/" + new_location["name"] + "/"] = {
                      "add_header": "Access-Control-Allow-Origin *",
                      "rewrite": f"(.*)/{new_location['name']}/resized_images/(.*)$ $1/{new_location['name']}/$2",
                      "alias": f"/usr/share/nginx/{new_location['directory']}/"
                    }
                else:
                    value["/" + new_location["name"] + "/"] = {
                      "add_header": "Access-Control-Allow-Origin *",
                      "alias": f"/usr/share/nginx/{new_location['directory']}/"
                    }
            else:
                recursive_search_of_locations(value, new_location)


if __name__ == "__main__":
    if ENV_FILE_LOCATION not in os.environ:
        # Try to load /.env file
        choice = input("Do you want to load /.env file? (y/n) ")
        if choice.lower() == "y" and os.path.exists("/.env"):
            load_dotenv("/.env")
        else:
            print("export .env file location as ENV_FILE_LOCATION. Export $HOME/image-viz/.env if running outside "
                  "of docker container, export /.env if running inside docker container backend.")
            sys.exit(1)
    else:
        # Load environment variables
        load_dotenv(os.getenv(ENV_FILE_LOCATION))

    # Get new location
    new_location = parsing()
    if new_location["directory"] == "" or new_location["name"] == "":
        print("No name or directory provided.")
        sys.exit(1)

    # Load nginx configuration json file
    with open(os.path.join(os.getenv(HOME), NGINX_CONF_JSON_NAME)) as f:
        nginx_config = json.load(f)
        # Now parse it and add the new location to the nginx configuration file
        recursive_search_of_locations(nginx_config, new_location)

    # Save the new configuration in nginx.conf.json
    with open(os.path.join(os.getenv(HOME), NGINX_CONF_JSON_NAME), "w") as f:
        json.dump(nginx_config, f, indent=4)
