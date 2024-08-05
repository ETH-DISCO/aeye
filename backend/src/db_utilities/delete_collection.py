import os
import sys

from dotenv import load_dotenv
from pymilvus import Collection
from pymilvus import utility, db

from .utils import create_connection
from ..CONSTANTS import *


def delete_collection():
    try:
        # Choose a database and switch to the newly created database
        db_name = input("Database name: (enter for default database): ")
        if db_name == "":
            db_name = DEFAULT_DATABASE_NAME

        if db_name not in db.list_database():
            print(f"No database named {db_name}.")
            sys.exit(1)

        db.using_database(db_name)

        # Get list of collections
        collections = utility.list_collections()
        print("Collections: ")
        for i, collection in enumerate(collections):
            print(f"{i + 1}. {collection}")

        index = int(input("Enter the index of the collection you want to delete: ")) - 1
        if index < 0 or index >= len(collections):
            print("Invalid index.")
            sys.exit(1)

        collection_name = collections[index]
        choice = input(f"The collection has {Collection(collection_name).num_entities} entities. "
                       f"Are you sure you want to delete it? (y/n)")
        if choice.lower() == "y":
            utility.drop_collection(collection_name)
            print("Collection dropped.")
        elif choice.lower() == "n":
            print("Operation aborted.")
        else:
            print("Invalid choice.")

    except Exception as e:
        print(e.__str__())
        sys.exit(1)


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
    try:
        create_connection(ROOT_USER, ROOT_PASSWD)
    except Exception as e:
        print("Error in main. Connection failed. Error: ", e)
        sys.exit(1)

    # Delete collection
    delete_collection()
