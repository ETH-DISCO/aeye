import json
import os

import dotenv
from pymilvus import utility, db
import requests

from backend.src.CONSTANTS import *
from backend.src.db_utilities.collections import ZOOM_LEVEL_VECTOR_FIELD_NAME
from backend.src.db_utilities.utils import create_connection

create_connection(ROOT_USER, ROOT_PASSWD)
db.using_database(DEFAULT_DATABASE_NAME)


def test_get_collection_names():
    # Load dataset options from datasets.json
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "r") as f:
        datasets = json.load(f)["datasets"]

    response = requests.get("http://localhost:32145/api/collection-names")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response.keys() == {"collections"}
    assert isinstance(json_response["collections"], list)
    assert len(json_response["collections"]) == len([dataset for dataset in datasets if dataset["name"]
                                                     in utility.list_collections()])


def test_get_collection_info():
    # Create request
    response = requests.get("http://localhost:32145/api/collection-info", params={"collection": "best_artworks"})
    assert response.status_code == 200
    assert response.json() == {"number_of_entities": 7947, "zoom_levels": 7}

    # Make second request to test that status code is 404 when collection is not found
    response = requests.get("http://localhost:32145/api/collection-info", params={"collection": "test_collection"})
    assert response.status_code == 404


def test_get_image_from_text():
    # Create Text object
    text = "A painting of a dog."
    response = requests.get("http://localhost:32145/api/image-text",
                            params={"text": text, "collection": "best_artworks"})
    assert response.status_code == 200
    assert response.json().keys() == {"index", "author", "path", "x", "y", "width", "height", "caption"}
    assert response.json()["path"] == "2881-Henri_de_Toulouse-Lautrec.jpg"
    assert response.json()["author"] == "Henri de Toulouse"


def test_get_tiles():
    response = requests.get("http://localhost:32145/api/tiles",
                            params={"indexes": [34, 557], "collection": "best_artworks_zoom_levels_clusters"})
    assert response.status_code == 200
    # Check that the response is a list
    assert isinstance(response.json(), list)
    # Check that the response has the same length as the request
    assert len(response.json()) == 1
    # Check that the response has the same keys as the request
    for i in range(len(response.json())):
        assert response.json()[i].keys() == {"index", "data"}

    # Make second request to test that status code is 404 when collection is not found
    response = requests.get("http://localhost:32145/api/tiles",
                            params={"indexes": [2881, 5432], "collection": "test_collection"})
    assert response.status_code == 404


def test_get_tile_from_image():
    response = requests.get("http://localhost:32145/api/image-to-tile",
                            params={"index": 1, "collection": "best_artworks_image_to_tile"})
    assert response.status_code == 200
    assert response.json().keys() == {"index", ZOOM_LEVEL_VECTOR_FIELD_NAME}
    assert response.json()[ZOOM_LEVEL_VECTOR_FIELD_NAME] == [7, 112, 22]

    # Make second request to test that status code is 404 when collection is not found
    response = requests.get("http://localhost:32145/api/image-to-tile",
                            params={"index": 2881, "collection": "test_collection"})
    assert response.status_code == 404
    # Check that the server returns 404 when the tile data is not found
    response = requests.get("http://localhost:32145/api/image-to-tile",
                            params={"index": 8000, "collection": "best_artworks_image_to_tile"})
    assert response.status_code == 404


def test_get_images():
    response = requests.get("http://localhost:32145/api/images",
                            params={"indexes": [2881, 5432], "collection": "best_artworks"})
    assert response.status_code == 200
    assert response.json() == [{"index": 2881, "path": "2881-Henri_de_Toulouse-Lautrec.jpg"},
                               {"index": 5432, "path": "5432-Pierre-Auguste_Renoir.jpg"}]
    # Make second request to test that status code is 404 when collection is not found
    response = requests.get("http://localhost:32145/api/images",
                            params={"indexes": [2881, 5432], "collection": "test_collection"})
    assert response.status_code == 404


def test_get_neighbours():
    response = requests.get("http://localhost:32145/api/neighbors",
                            params={"index": 2881, "k": 10, "collection": "best_artworks"})
    assert response.status_code == 200
    assert len(response.json()) == 11
    assert response.json()[0].keys() == {"index", "author", "path", "width", "height", "caption"}

    # Make second request to test that status code is 404 when collection is not found
    response = requests.get("http://localhost:32145/api/neighbours",
                            params={"index": 2881, "collection": "test_collection"})
    assert response.status_code == 404


def test_get_first_tiles():
    response = requests.get("http://localhost:32145/api/first-tiles",
                            params={"collection": "best_artworks_zoom_levels_clusters"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Check keys
    assert response.json()[0].keys() == {"index", "data", "range"}
    for i in range(1, len(response.json())):
        assert response.json()[i].keys() == {"index", "data"}

    assert list(response.json()["clusters"][0]["range"].keys()) == ['x_min', 'x_max', 'y_min', 'y_max']

    # Make second request to test that status code is 404 when collection is not found
    response = requests.get("http://localhost:32145/api/first-tiles",
                            params={"collection": "test_collection"})
    assert response.status_code == 404


def test_get_image_from_image():
    dotenv.load_dotenv(os.getenv(ENV_FILE_LOCATION))
    url = "http://localhost:32145/api/image-image"
    params = {"collection": "best_artworks"}
    file_path = f"{os.getenv(HOME)}/best_artworks/1-Alfred_Sisley.jpg"

    with open(file_path, "rb") as f:
        response = requests.post(url, params=params, files={"file": f})

    assert response.status_code == 200
    assert response.json().keys() == {'index', 'author', 'path', 'width', 'height', 'caption', 'x', 'y'}
