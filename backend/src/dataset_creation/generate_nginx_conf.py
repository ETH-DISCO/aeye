import json
import os

from ..CONSTANTS import *


def recursive_parse(nginx_config, level=0, add_location=False):
    # If add_location is True, add "location" before the key in the configuration file.
    location = ""
    if add_location:
        location = "location "

    for key, value in nginx_config.items():
        # If the key starts with a number, remove it.
        if key[0].isdigit():
            key = key[1:]

        if isinstance(value, dict):
            # Check if the key is "locations". If so, avoid adding "locations" to the configuration file and recursively
            # parse the value of the "locations" key, using add_location=True.
            if key == "locations":
                recursive_parse(value, level, add_location=True)
                continue

            if not list(value.keys())[0].startswith("_"):
                print("    " * level + location + key + " {")
                recursive_parse(value, level + 1)
                print("    " * level + "}")

            else:
                # The value is the name of the current key. Put it right after the key.
                assert len(value.keys()) == 1
                value_without_first_underscore = list(value.keys())[0][1:]
                if isinstance(list(value.values())[0], dict):
                    print("    " * level + location + key + " " + value_without_first_underscore + " {")
                    recursive_parse(list(value.values())[0], level + 1)
                    print("    " * level + "}")
                else:
                    print("    " * level + location + key + " " + value_without_first_underscore + " "
                          + str(list(value.values())[0]) + ";")

        else:
            print("    " * level + location + str(key) + " " + str(value) + ";")


if __name__ == "__main__":
    # Load nginx configuration json file
    with open(os.path.join(os.getenv(HOME), NGINX_CONF_JSON_NAME), "r") as f:
        nginx_config = json.load(f)
        # Now parse it and generate the nginx configuration file
        recursive_parse(nginx_config)
