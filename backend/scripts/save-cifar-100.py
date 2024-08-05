from PIL import Image
import os
import sys
from dotenv import load_dotenv
from ..src.CONSTANTS import ENV_FILE_LOCATION, HOME


def unpickle(file):
    import pickle
    with open(file, 'rb') as fo:
        d = pickle.load(fo, encoding='bytes')
    return d


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

    # Get training images
    file_path = os.getenv(HOME) + "/CIFAR-100/train"
    # Unpickle the file
    data = unpickle(file_path)
    # Get raw data
    data = data[b'data']

    index = 0
    # Save images to os.getenv(HOME) + "/mnist-dataset directory as index.png
    for image in data:
        # Reshape image to 3x32x32
        img = image.reshape(3, 32, 32).transpose([1, 2, 0])
        img = Image.fromarray(img)
        img.save(os.getenv(HOME) + "/CIFAR-100/" + str(index) + ".png")
        index += 1

    # Get test images
    file_path = os.getenv(HOME) + "/CIFAR-100/test"
    # Unpickle the file
    data = unpickle(file_path)
    # Get raw data
    data = data[b'data']

    for image in data:
        # Reshape image to 3x32x32
        img = image.reshape(3, 32, 32).transpose([1, 2, 0])
        img = Image.fromarray(img)
        img.save(os.getenv(HOME) + "/CIFAR-100/" + str(index) + ".png")
        index += 1

    # Remove both train-images.idx3-ubyte and t10k-images.idx3-ubyte
    os.remove(os.getenv(HOME) + "/CIFAR-100/train")
    os.remove(os.getenv(HOME) + "/CIFAR-100/test")
    print("Images saved.")
