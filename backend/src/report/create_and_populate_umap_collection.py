import getopt
import json
import os
import sys
import warnings

from dotenv import load_dotenv
from pymilvus import db, Collection, utility
from umap import UMAP

from ..CONSTANTS import *
from ..db_utilities.collections import EMBEDDING_VECTOR_FIELD_NAME, umap_collection
from ..db_utilities.utils import create_connection


def parsing():
    # Load dataset options from datasets.json
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "r") as f:
        datasets = json.load(f)["datasets"]
    # Remove 1st argument from the list of command line arguments
    arguments = sys.argv[1:]
    # Options
    options = "h"
    # Long options
    long_options = ["help"]
    # Prepare flags
    flags = {"dataset": datasets[1]["name"], "database": DEFAULT_DATABASE_NAME}

    # Parsing argument
    arguments, values = getopt.getopt(arguments, options, long_options)

    if len(arguments) > 0 and arguments[0][0] in ("-h", "--help"):
        print(
            f'This script generates scatter plots of low dimensional embeddings for '
            f'{datasets[1]["name"]} dataset.')
        sys.exit(0)

    return flags


def generate_scatter_plots(collection: Collection):
    print("Generating scatter plots data...")
    # Load collection in memory
    collection.load()

    if collection.num_entities == 0:
        print("Collection is empty. Scatter plots generation failed!")
        return

    # Fetch vectors
    entities = []
    try:
        for i in range(0, collection.num_entities, SEARCH_LIMIT):
            # Get SEARCH_LIMIT entities
            query_result = collection.query(
                expr=f"index in {list(range(i, min(i + SEARCH_LIMIT, collection.num_entities)))}",
                output_fields=[EMBEDDING_VECTOR_FIELD_NAME]
            )
            # Add entities to the list of entities
            entities += query_result

    except Exception as e:
        print(e.__str__())
        print("Error in fetching vectors. Scatter plots generation failed!")
        return

    # Create scatter plot
    data = [entity[EMBEDDING_VECTOR_FIELD_NAME] for entity in entities]

    # Create UMAP collection
    umap_c = umap_collection(UMAP_COLLECTION_NAME, collection.num_entities)

    # Loop over neighbors and min_dist and generate scatter plots
    umap_data = []
    index = 0
    for n in N_NEIGHBORS:
        for m in MIN_DISTS:
            datapoint = {"n_neighbors": n, "min_dist": m, "index": index}
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                reducer = UMAP(n_neighbors=n, n_components=2, min_dist=m, random_state=RANDOM_STATE, n_jobs=1)
                low_dim_data = reducer.fit_transform(data)
            datapoint["data"] = [p for point in low_dim_data for p in point]
            assert len(datapoint["data"]) == 2 * collection.num_entities
            umap_data.append(datapoint)
            print(f"Generated scatter plot for n_neighbors={n}, min_dist={m}.")
            index += 1

    # Insert data into UMAP collection
    try:
        umap_c.insert([datapoint for datapoint in umap_data])
        umap_c.flush()
    except Exception as e:
        print(e.__str__())
        print("Error in inserting data into UMAP collection. Scatter plots generation failed!")
        utility.drop_collection(umap_c.name)
        return

    print("Scatter plots data generated and inserted into UMAP collection.")
    return


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

    # Get the collection object
    collection_name = flags["dataset"]
    collection = Collection(collection_name)

    print(f"Using collection {collection_name}. The collection contains {collection.num_entities} entities.")

    generate_scatter_plots(collection)
    sys.exit(0)
