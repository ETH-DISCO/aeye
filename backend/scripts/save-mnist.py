import argparse
import os
import sys

import idx2numpy
from PIL import Image
from dotenv import load_dotenv

from ..src.CONSTANTS import ENV_FILE_LOCATION, HOME


def execute_cmdline(argv):
    prog = argv[0]
    parser = argparse.ArgumentParser(
        prog=prog,
        description='Tool for saving MNIST dataset as images.',
        epilog='Type "%s <command> -h" for more information.' % prog)
    # Add directory argument
    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        help="Directory of the MNIST dataset.",
        required=True,
        default="MNIST"
    )
    args = parser.parse_args(argv[1:])
    return args


if __name__ == "__main__":
    # Load environment variables
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
    args = execute_cmdline(sys.argv)

    # Get training images
    file_path = os.getenv(HOME) + "/" + args.directory + "/train-images.idx3-ubyte"
    train = idx2numpy.convert_from_file(file_path)

    index = 0
    # Save images
    for image in train:
        im = Image.fromarray(image)
        im.save(os.getenv(HOME) + f"/{args.directory}/" + str(index) + ".png")
        index += 1

    # Get test images
    file_path = os.getenv(HOME) + "/" + args.directory + "/t10k-images.idx3-ubyte"
    test = idx2numpy.convert_from_file(file_path)

    for image in test:
        im = Image.fromarray(image)
        im.save(os.getenv(HOME) + f"/{args.directory}/" + str(index) + ".png")
        index += 1

    # Remove both train-images.idx3-ubyte and t10k-images.idx3-ubyte
    os.remove(os.getenv(HOME) + "/" + args.directory + "/train-images.idx3-ubyte")
    os.remove(os.getenv(HOME) + "/" + args.directory + "/t10k-images.idx3-ubyte")
    print("Images saved.")
