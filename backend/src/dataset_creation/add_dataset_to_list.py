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
    options = "hd:c:l:f:s:w:"
    # Long options
    long_options = ["help", "database", "dataset", "dir_name", "collate_fn", "dataset_class", "website_name"]

    # Parsing argument
    arguments, values = getopt.getopt(arguments, options, long_options)

    flags = {"database": DEFAULT_DATABASE_NAME, "dataset": None}

    if len(arguments) > 0 and arguments[0][0] in ("-h", "--help"):
        print(f'This script checks if a dataset exists in the database.\n\
        -d or --database: database name (default={flags["database"]}).\n\
        -c or --dataset: dataset.\n\
        -l or --dir_name: directory name.\n\
        -f or --collate_fn: collate function.\n\
        -s or --dataset_class: dataset class.\n\
        -w or --website_name: website name.')
        sys.exit(0)

    # Checking each argument
    for arg, val in arguments:
        if arg in ("-d", "--database"):
            flags["database"] = val
        elif arg in ("-c", "--dataset"):
            flags["dataset"] = val
        elif arg in ("-l", "--dir_name"):
            flags["dir_name"] = val
        elif arg in ("-f", "--collate_fn"):
            flags["collate_fn"] = val
        elif arg in ("-s", "--dataset_class"):
            flags["dataset_class"] = val
        elif arg in ("-w", "--website_name"):
            flags["website_name"] = val

    return flags


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

    # Get arguments
    flags = parsing()

    # Open dataset.json file
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "r") as f:
        datasets = json.load(f)

    # If the list of datasets already contains the dataset, update its values
    if flags["dataset"] in [d["name"] for d in datasets["datasets"]]:
        for dataset in datasets["datasets"]:
            if dataset["name"] == flags["dataset"]:
                dataset["collate_fn"] = flags["collate_fn"]
                dataset["dataset_class"] = flags["dataset_class"]
                dataset["dir_name"] = flags["dir_name"]
                dataset["website_name"] = flags["website_name"]
                break
    else:
        # Add dataset to list
        datasets["datasets"].append(
            {
                "name": flags["dataset"],
                "collate_fn": flags["collate_fn"],
                "zoom_levels": -1,
                "dataset_class": flags["dataset_class"],
                "dir_name": flags["dir_name"],
                "website_name": flags["website_name"]
            }
        )

    # Save dataset.json file
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "w") as f:
        json.dump(datasets, f, indent=4)
