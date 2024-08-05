import sys

from pymilvus import utility, db

from .utils import create_connection
from ..CONSTANTS import *

if __name__ == "__main__":
    database = DEFAULT_DATABASE_NAME
    # Try creating a connection and selecting a database. If it fails, exit.
    choice = input("Select database (enter to keep default): ")
    if choice != "":
        database = choice
    try:
        create_connection(ROOT_USER, ROOT_PASSWD)
        db.using_database(database)
    except Exception as e:
        print("Error in main. Connection failed. Error: ", e)
        sys.exit(1)

    # Get the collection object
    old_collection_name = input("Enter the old collection name: ")
    new_collection_name = input("Enter the new collection name: ")
    # Rename collection
    utility.rename_collection(old_collection_name, new_collection_name, new_db_name=database)
