import getopt
import json
import os
import sys

from dotenv import load_dotenv
from matplotlib import pyplot as plt
from pymilvus import db, Collection

from ..CONSTANTS import *
from ..db_utilities.utils import create_connection


def parsing():
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "r") as f:
        datasets = json.load(f)["datasets"]

    # Remove 1st argument from the list of command line arguments
    arguments = sys.argv[1:]

    # Options
    options = "hd:c:"

    # Long options
    long_options = ["help", "database", "dataset"]

    # Prepare flags
    flags = {"database": DEFAULT_DATABASE_NAME, "dataset": datasets[0]["name"], "directory": datasets[0]["dir_name"]}

    # Parsing argument
    arguments, values = getopt.getopt(arguments, options, long_options)

    if len(arguments) > 0 and arguments[0][0] in ("-h", "--help"):
        print(f'This script generates a scatter plot of low dimensional embedding for a dataset.\n\
        -d or --database: database name (default={flags["database"]}).\n\
        -c or --dataset: dataset (default={flags["dataset"]}).')
        sys.exit(0)

    # Checking each argument
    for arg, val in arguments:
        if arg in ("-d", "--database"):
            flags["database"] = val
        elif arg in ("-c", "--dataset"):
            if val in [dataset["name"] for dataset in datasets]:
                flags["dataset"] = val
                for dataset in datasets:
                    if dataset["name"] == val:
                        flags["directory"] = dataset["dir_name"]
                        break
            else:
                print("Dataset not supported.")
                sys.exit(1)

    return flags


def generate_scatter_plot(flags: dict):
    # Get the collection object
    collection = Collection(flags["dataset"])

    print("Generating scatter plot...")
    # Load collection in memory
    collection.load()

    # Fetch vectors
    entities = []
    try:
        for i in range(0, collection.num_entities, SEARCH_LIMIT):
            if collection.num_entities > 0:
                # Get SEARCH_LIMIT entities
                query_result = collection.query(
                    expr=f"index in {list(range(i, i + SEARCH_LIMIT))}",
                    output_fields=["x", "y"]
                )
                # Add entities to the list of entities
                entities += query_result

    except Exception as e:
        print(e.__str__())
        print("Error in fetching vectors. Scatter plot generation failed!")
        return

    # Create scatter plot
    x = [entity["x"] for entity in entities]
    y = [-entity["y"] for entity in entities]

    # Create figure
    fig, ax = plt.subplots(figsize=(20, 12))

    # Set x and y limits to the minimum and maximum values of your data
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))

    # Create scatter plot with blue dots
    ax.scatter(x, y, s=3, c="lightblue")

    # Remove all axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Remove all labels
    ax.set_xticks([])
    ax.set_yticks([])

    # Make background black
    ax.set_facecolor("black")

    # Remove all white space on the plot
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Save scatter plot
    directory = os.path.join(os.getenv(HOME), flags["directory"])
    if not os.path.exists(directory):
        print("We could not find the directory to save the scatter plot.")
        sys.exit(1)

    plt.savefig(os.path.join(directory, "minimap.png"))
    print(f"Minimap saved for collection {collection.name} at {os.path.join(directory, 'minimap.png')}.")

    # Release collection
    collection.release()


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

    # Try creating a connection and selecting a database. If it fails, exit.
    try:
        create_connection(ROOT_USER, ROOT_PASSWD, False)
        db.using_database(flags["database"])
    except Exception as e:
        print(e.__str__())
        print("Error in main. Connection failed!")
        sys.exit(1)

    generate_scatter_plot(flags)
    sys.exit(0)
