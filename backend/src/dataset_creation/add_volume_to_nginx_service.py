import getopt
import os
import sys

from ruamel.yaml import YAML
from dotenv import load_dotenv

from ..CONSTANTS import *


def parsing():
    # Remove 1st argument from the list of command line arguments
    arguments = sys.argv[1:]

    # Options
    options = "hd:"

    # Long options
    long_options = ["help", "directory"]

    # Parsing argument
    arguments, values = getopt.getopt(arguments, options, long_options)

    if len(arguments) > 0 and arguments[0][0] in ("-h", "--help"):
        print(f'This script adds a new volume to the docker-compose.yml file.\n\
        -d or --directory: directory for new location.')
        sys.exit()

    # Checking each argument
    for arg, val in arguments:
        if arg in ("-d", "--directory"):
            return val

    return None


def search_for_nginx_volumes(docker_compose, directory):
    # Search for the "volumes" key in the nginx service in the docker-compose file and add the new value to it.
    for key, value in docker_compose.items():
        if key == "services":
            for service, service_value in value.items():
                if service == "nginx":
                    if "volumes" in service_value:
                        if f"../{directory}:/usr/share/nginx/{directory}" not in service_value["volumes"]:
                            service_value["volumes"].append(f"../{directory}:/usr/share/nginx/{directory}")
                    else:
                        service_value["volumes"] = [f"{directory}:/usr/share/nginx/{directory}"]


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
    directory = parsing()
    if directory is None:
        print("Directory not provided.")
        sys.exit(1)

    # Load docker-compose.yml file
    yaml = YAML()
    yaml.default_flow_style = False
    # Keep indentation of the file
    yaml.indent(mapping=2, sequence=4, offset=2)
    # Keep double quotes
    yaml.preserve_quotes = True
    # Allow lines to be longer than 80 characters
    yaml.width = 1000
    with open(os.path.join(os.getenv(HOME), DOCKER_COMPOSE_YML_NAME), "r") as file:
        docker_compose = yaml.load(file)
        # Add new volume to the nginx service
        search_for_nginx_volumes(docker_compose, directory)

    # Write to docker-compose.yml file
    with open(os.path.join(os.getenv(HOME), DOCKER_COMPOSE_YML_NAME), "w") as file:
        yaml.dump(docker_compose, file)
