import getopt
import json
import os
import sys

import PIL.Image
from dotenv import load_dotenv

from .CONSTANTS import *

# Increase pixel limit
PIL.Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


def parsing():
    # Load dataset options from datasets.json
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "r") as f:
        datasets = json.load(f)["datasets"]

    # Remove 1st argument from the list of command line arguments
    arguments = sys.argv[1:]

    # Options
    options = "hd:o:"

    # Long options
    long_options = ["help", "dataset", "overwrite"]

    # Parsing argument
    arguments, values = getopt.getopt(arguments, options, long_options)

    flags = {"directory": None, "overwrite": False}

    if len(arguments) > 0 and arguments[0][0] in ("-h", "--help"):
        print(f'This script generates the resized images for a dataset.\n\
        -d or --dataset: dataset name.\n\
        -o or --overwrite: overwrite resized images directory if it already exists'
              f' (y/n, default={"n" if not flags["overwrite"] else "y"}).')
        sys.exit(0)

    # Checking each argument
    for arg, val in arguments:
        if arg in ("-d", "--dataset"):
            for dataset in datasets:
                if val == dataset["name"]:
                    flags["directory"] = dataset["dir_name"]
                    break
            if flags["directory"] is None:
                raise ValueError("Dataset not supported.")
        elif arg in ("-o", "--overwrite"):
            if val.lower() == "y":
                flags["overwrite"] = True
            elif val.lower() == "n":
                flags["overwrite"] = False
            else:
                raise ValueError("overwrite must be y or n.")

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
    try:
        flags = parsing()
    except ValueError as e:
        print(e)
        sys.exit(1)

    # Get directory path
    directory_path = os.path.join(os.getenv(HOME), flags["directory"])

    # First, check if the directory exists
    if not os.path.isdir(directory_path):
        print(f"Directory {directory_path} does not exist.")
        sys.exit(1)

    # Create subdirectory for resized images
    resized_images_dir = os.path.join(directory_path, "resized_images")
    if not os.path.isdir(resized_images_dir):
        os.mkdir(resized_images_dir)
    else:
        if flags["overwrite"]:
            print("Overwriting resized images directory.")
            # Delete contents of directory
            for filename in os.listdir(resized_images_dir):
                os.remove(os.path.join(resized_images_dir, filename))
        else:
            sys.exit(0)

    # Loop over files in dataset directory
    for filename in os.listdir(directory_path):
        try:
            # Check if file is an image
            if ((not (filename.endswith(".jpg") or filename.endswith(".png"))) or filename == "minimap.jpg"
                    or filename == "minimap.png"):
                continue
            # Load image
            image = PIL.Image.open(os.path.join(directory_path, filename))
            # Compute height and width using resizing factor
            aspect_ratio = image.width / image.height
            # Get width and height
            if image.width > image.height:
                width = max(image.width, RESIZING_WIDTH)
                height = int(width / aspect_ratio)
            else:
                height = max(image.height, RESIZING_HEIGHT)
                width = int(height * aspect_ratio)

            # Resize image
            image.thumbnail((width, height), PIL.Image.ANTIALIAS)
            # Save image
            image.save(os.path.join(resized_images_dir, filename))
        except Exception as e:
            print(f"Error resizing image {filename}: {e}")
            sys.exit(1)

    print("Done resizing images.")
