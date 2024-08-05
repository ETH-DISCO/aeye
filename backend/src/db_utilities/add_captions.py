import csv
import getopt
import json
import os
import sys

from dotenv import load_dotenv
from pymilvus import db, Collection, utility

from .collections import embeddings_collection
from .utils import create_connection
from ..CONSTANTS import *


def parsing():
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "r") as f:
        datasets = json.load(f)["datasets"]

    # Remove 1st argument from the list of command line arguments
    arguments = sys.argv[1:]

    # Options
    options = "hd:c:"
    # Long options
    long_options = ["help", "database", "collection"]

    # Prepare flags
    flags = {"database": DEFAULT_DATABASE_NAME, "collection": datasets[0]["name"]}

    # Parsing argument
    arguments, values = getopt.getopt(arguments, options, long_options)

    if len(arguments) > 0 and arguments[0][0] in ("-h", "--help"):
        print(f'This script adds captions to the entities in the collection.\n\
        -d or --database: database name (default={flags["database"]}).\n\
        -c or --collection: collection name (default={flags["collection"]}).')
        sys.exit(0)

    # Checking each argument
    for arg, val in arguments:
        if arg in ("-d", "--database"):
            flags["database"] = val
        elif arg in ("-c", "--collection"):
            if val in [dataset["name"] for dataset in datasets]:
                flags["collection"] = val
            else:
                print("The collection must have one of the following names: " + str([dataset["name"]
                                                                                     for dataset in datasets]))
                sys.exit(1)

    return flags


if __name__ == "__main__":
    if ENV_FILE_LOCATION not in os.environ:
        # Try to load /.env file
        if os.path.exists("/.env"):
            load_dotenv("/.env")
        else:
            print("export .env file location as ENV_FILE_LOCATION.")
            sys.exit(1)
    else:
        # Load environment variables
        load_dotenv(os.getenv(ENV_FILE_LOCATION))

    flags = parsing()

    # Try creating a connection and selecting a database. If it fails, exit.
    try:
        create_connection(ROOT_USER, ROOT_PASSWD, False)
        db.using_database(flags["database"])
    except Exception as e:
        print("Error in main. Connection failed. Error: ", e)
        sys.exit(1)

    # 1. Create a variable to store the path to the file
    PATH = f"{os.getenv(HOME)}/image-viz/backend/src/captioning/captions/captions_{flags['collection']}.csv"

    captions = {}
    # 2. Open the file
    with open(PATH, "r") as file:
        # 3. Create a csv reader object
        reader = csv.reader(file)
        header = next(reader)
        # 5. Loop over the rows
        for row in reader:
            # Get captions
            captions[int(row[0])] = row[1]

    # Get the collection object
    collection = Collection(flags["collection"])

    # Fetch vectors
    entities = []
    try:
        for i in range(0, collection.num_entities, SEARCH_LIMIT):
            if collection.num_entities > 0:
                # Get SEARCH_LIMIT entities
                query_result = collection.query(
                    expr=f"index in {list(range(i, i + SEARCH_LIMIT))}",
                    output_fields=["*"]
                )
                # Add entities to the list of entities
                entities += query_result
    except Exception as e:
        print("Error in update_metadata. Update failed. Error message: ", e)
        sys.exit(1)

    # Order entities by index
    entities = sorted(entities, key=lambda x: x["index"])
    # Assert that the indices are correct, i.e., the range is the same as the number of captions
    assert len(entities) == len(captions)

    # Add captions to entities
    # Update vectors
    for i in range(len(entities)):
        assert (entities[i]["index"] == i)
        entities[i]["caption"] = captions[entities[i]["index"]]

    # Define new name
    new_name = "temp_" + flags["collection"]
    try:
        # Create cluster collection
        new_collection = embeddings_collection(new_name)
        # Do for loop to avoid resource exhaustion
        for i in range(0, len(entities), INSERT_SIZE):
            new_collection.insert(data=entities[i:i + INSERT_SIZE])
        # Flush collection
        new_collection.flush()
    except Exception as e:
        print("Error in update_metadata. Update failed. Error message: ", e)
        utility.drop_collection(new_name)
        sys.exit(1)

    # Drop old collection and rename new collection
    try:
        # Drop old collection
        utility.drop_collection(flags["collection"])
        # Rename new collection
        utility.rename_collection(new_name, flags["collection"], new_db_name=flags["database"])
    except Exception as e:
        print("Error in update_metadata. Update failed. Error message: ", e)
        sys.exit(1)
