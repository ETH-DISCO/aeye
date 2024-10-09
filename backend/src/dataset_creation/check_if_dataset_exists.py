import getopt
import sys

from pymilvus import utility, db

from ..CONSTANTS import *
from ..db_utilities.utils import create_connection


def parsing():
    # Remove 1st argument from the list of command line arguments
    arguments = sys.argv[1:]

    # Options
    options = "hd:c:"
    # Long options
    long_options = ["help", "database", "dataset"]

    # Parsing argument
    arguments, values = getopt.getopt(arguments, options, long_options)

    flags = {"database": DEFAULT_DATABASE_NAME, "dataset": None}

    if len(arguments) > 0 and arguments[0][0] in ("-h", "--help"):
        print(f'This script checks if a dataset exists in the database.\n\
        -d or --database: database name (default={flags["database"]}).\n\
        -c or --dataset: dataset.')
        sys.exit(0)

    # Checking each argument
    for arg, val in arguments:
        if arg in ("-d", "--database"):
            flags["database"] = val
        if arg in ("-c", "--dataset"):
            flags["dataset"] = val

    return flags


if __name__ == "__main__":
    # Get arguments
    flags = parsing()

    if flags["dataset"] is None:
        print("Dataset not provided.")
        sys.exit(1)

    # Try creating a connection and selecting a database. If it fails, exit.
    try:
        # Create connection and select database
        create_connection(ROOT_USER, ROOT_PASSWD)
        # Create the database if it does not exist
        if DEFAULT_DATABASE_NAME not in db.list_database():
            print(f"Database {DEFAULT_DATABASE_NAME} does not exist. Creating it...")
            db.create_database(DEFAULT_DATABASE_NAME)
            print("Database created.")

        # Use the database
        db.using_database(DEFAULT_DATABASE_NAME)
        # Check if dataset exists
        if not utility.has_collection(flags["dataset"]):
            print("All good.")
        else:
            print(f"Dataset {flags['dataset']} exists.")

    except Exception as e:
        print("Error in checking if dataset exists. Error message: ", e)
        sys.exit(1)
