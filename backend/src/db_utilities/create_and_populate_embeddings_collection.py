import getopt
import json
import os
import sys
import warnings

import PIL.Image
import torch
from dotenv import load_dotenv
from pymilvus import utility, db, Collection

from .DatasetPreprocessor import DatasetPreprocessor
from .collections import embeddings_collection, EMBEDDING_VECTOR_FIELD_NAME
from .datasets import get_dataset_object
from .utils import create_connection
from ..CONSTANTS import *
from ..embeddings_model.CLIPEmbeddings import ClipEmbeddings

# Increase pixel limit
PIL.Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


def parsing():
    # Load dataset options from datasets.json
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "r") as f:
        datasets = json.load(f)["datasets"]
    # Remove 1st argument from the list of command line arguments
    arguments = sys.argv[1:]

    # Options
    options = "hd:c:b:r:"

    # Long options
    long_options = ["help", "database", "collection", "batch_size", "repopulate"]

    # Prepare flags
    flags = {"database": DEFAULT_DATABASE_NAME, "dataset": datasets[0]["name"],
             "batch_size": BATCH_SIZE, "repopulate": False}

    # Parsing argument
    arguments, values = getopt.getopt(arguments, options, long_options)

    if len(arguments) > 0 and arguments[0][0] in ("-h", "--help"):
        print(f'This script populates a collection with embeddings.\n\
        -d or --database: database name (default={flags["database"]}).\n\
        -c or --collection: dataset (default={flags["dataset"]}).\n\
        -b or --batch_size: batch size used for loading the dataset (default={BATCH_SIZE}).\n\
        -r or --repopulate: whether to empty the database and repopulate. Type y for repopulating the store, '
              f'n otherwise (default={"n" if not flags["repopulate"] else "y"}).')
        sys.exit()

    # Checking each argument
    for arg, val in arguments:
        if arg in ("-d", "--database"):
            flags["database"] = val
        elif arg in ("-c", "--collection"):
            if val in [d["name"] for d in datasets]:
                flags["dataset"] = val
            else:
                print("Dataset not found.")
                sys.exit(1)
        elif arg in ("-b", "--batch_size"):
            if int(val) >= 1:
                flags["batch_size"] = int(val)
            else:
                print("Batch size must be greater than 0.")
                sys.exit(1)
        elif arg in ("-r", "--repopulate"):
            if val.lower() == "y":
                flags["repopulate"] = True
            elif val.lower() == "n":
                flags["repopulate"] = False
            else:
                print("Repopulate must be either y or n.")
                sys.exit(1)

    return flags


def modify_data(data: dict) -> list:
    # Get data keys
    keys = list(data.keys())

    # Checks that data is conforming to requirements.
    if "embeddings" not in keys:
        print("Embeddings are not in data.")
        sys.exit(1)
    if "index" not in keys:
        print("Indexes are not in data")
        sys.exit(1)
    if len(data["embeddings"].shape) != 2:
        print("'embeddings' should form a matrix.")
        sys.exit(1)
    for key in keys:
        if key != "embeddings":
            if len(data[key]) != data["embeddings"].shape[0]:
                print(f"Attributes should match the number of embeddings, but this is not true for {key}.")
                sys.exit(1)

    # Remove embeddings and index from keys
    keys.remove("embeddings")
    keys.remove("index")

    new_data = []
    for i in range(0, data["embeddings"].shape[0]):
        new_data.append(
            {
                "index": data["index"][i],
                EMBEDDING_VECTOR_FIELD_NAME: data["embeddings"][i].tolist(),
                "x": 0,
                "y": 0,
                **{key: data[key][i] for key in keys}
            }
        )

    return new_data


def generate_low_dimensional_embeddings(entities: list, dp: DatasetPreprocessor, collection_name: str):
    # Process records
    embeddings = torch.tensor([entities[i][EMBEDDING_VECTOR_FIELD_NAME] for i in range(len(entities))]).detach()

    # Set embeddings
    dp.setEmbeddings(embeddings)
    # Get metadata
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        data = dp.generateRecordsMetadata()

    # Update vectors
    for i in range(len(entities)):
        entities[i]["x"] = data["low_dim_embeddings"][i][0]
        entities[i]["y"] = data["low_dim_embeddings"][i][1]

    # Create collection
    try:
        collection = embeddings_collection(collection_name)
    except Exception as e:
        print("Error in creation of embeddings collection. Error message: ", e)
        sys.exit(1)

    try:
        # Do for loop to avoid resource exhaustion
        for i in range(0, len(entities), INSERT_SIZE):
            collection.insert(data=entities[i:i + INSERT_SIZE])
        # Flush the collection
        collection.flush()
    except Exception as e:
        print("Error in generate_low_dimensional_embeddings. Error message: ", e)
        sys.exit(1)

    # Release collection
    collection.release()


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

    # Get arguments
    flags = parsing()

    # Try creating a connection and selecting a database. If it fails, exit.
    try:
        create_connection(ROOT_USER, ROOT_PASSWD, False)
        db.using_database(flags["database"])
    except Exception as e:
        print("Error in main. Connection failed. Error: ", e)
        sys.exit(1)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        if utility.has_collection(flags["dataset"]) and (flags["repopulate"]
                                                         or Collection(flags["dataset"]).num_entities == 0):
            utility.drop_collection(flags["dataset"])
        elif utility.has_collection(flags["dataset"]) and not (flags["repopulate"]
                                                               or Collection(flags["dataset"]).num_entities == 0):
            print(f"Found collection {flags['dataset']}. It has more than 0 entities."
                  f" Set repopulate to True to drop it.")
            sys.exit(0)

        # Get dataset object
        dataset = get_dataset_object(flags["dataset"])
        # Create an embedding object
        embeddings = ClipEmbeddings(device=DEVICE)
        # Create dataset preprocessor
        dp = DatasetPreprocessor(embeddings)
        # Get dataloader
        dataloader = dataset.get_dataloader(flags["batch_size"], NUM_WORKERS, embeddings.processData)
        # Generate data
        data = dp.generateDatabaseEmbeddings(dataloader)
        # Get entities
        entities = modify_data(data)
        # Generate low dimensional embeddings
        generate_low_dimensional_embeddings(entities, dp, flags["dataset"])

        print(f"Embeddings collection created and populated for dataset {flags['dataset']}.")
        sys.exit(0)
