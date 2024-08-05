import getopt
import json
import os
import sys

import numpy as np
from PIL import Image
from dotenv import load_dotenv
from pymilvus import db, Collection, utility
from tqdm import tqdm

from .collections import clusters_collection, image_to_tile_collection, ZOOM_LEVEL_VECTOR_FIELD_NAME
from .utils import ModifiedKMeans
from .utils import create_connection
from ..CONSTANTS import *

# Increase pixel limit
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

MAX_IMAGES_PER_TILE = 30
NUMBER_OF_CLUSTERS = 30
# THRESHOLD = 0.8
LIMIT_FOR_TOTAL = 8000000
LIMIT_FOR_KEEP = 4000000
LIMIT_FOR_FETCH = 200000


def parsing():
    # Load dataset options from datasets.json
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "r") as f:
        datasets = json.load(f)["datasets"]

    # Remove 1st argument from the list of command line arguments
    arguments = sys.argv[1:]

    # Options
    options = "hd:c:r:"
    # Long options
    long_options = ["help", "database", "collection", "repopulate"]

    # Prepare flags
    flags = {"database": DEFAULT_DATABASE_NAME,
             "collection": datasets[0]["name"],
             "repopulate": False}

    # Parsing argument
    arguments, values = getopt.getopt(arguments, options, long_options)

    if len(arguments) > 0 and arguments[0][0] in ("-h", "--help"):
        print(f'This script generates zoom levels.\n\
        -d or --database: database name (default={flags["database"]}).\n\
        -c or --collection: collection name (default={flags["collection"]}).\n\
        -r or --repopulate: repopulate the collection. Options are y/n (default='
              f'{"y" if flags["repopulate"] == "y" else "n"}).')
        sys.exit(0)

    # Checking each argument
    for arg, val in arguments:
        if arg in ("-d", "--database"):
            flags["database"] = val
        elif arg in ("-c", "--collection"):
            if val in [d["name"] for d in datasets]:
                flags["collection"] = val
            else:
                print("The collection must have one of the following names: "
                      + str([d["name"] for d in datasets]))
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


def load_vectors_from_collection(collection: Collection) -> list:
    # Load collection in memory
    collection.load()
    # Get attributes
    attributes = (["index", "path", "width", "height", "x", "y"])

    # Get elements from collection
    entities = []
    try:
        for i in range(0, collection.num_entities, SEARCH_LIMIT):
            if collection.num_entities > 0:
                # Get SEARCH_LIMIT entities
                query_result = collection.query(
                    expr=f"index in {list(range(i, i + SEARCH_LIMIT))}",
                    output_fields=attributes
                )
                # Add entities to the list of entities
                entities += query_result
    except Exception as e:
        print("Error in load_vectors_from_collection. Error message: ", e)
        collection.release()
        sys.exit(1)

    collection.release()
    # Now entities contains all the entities in the collection, with fields 'index' and 'low_dimensional_embedding_*'
    return entities


def get_index_from_tile(zoom_level, tile_x, tile_y):
    index = 0
    for i in range(zoom_level):
        index += 4 ** i
    index += 2 ** zoom_level * tile_x + tile_y
    return index


def insert_vectors_in_clusters_collection(zoom_levels, images_to_tile, collection: Collection, entities_per_zoom_level,
                                          zoom_level, current_tile_x, current_tile_y, last_call=False) -> bool:
    try:
        # Define list of entities to insert in the collection
        entities_to_insert = []
        # Iterate over elements in zoom_levels
        for zoom in zoom_levels.keys():
            for tile_x in zoom_levels[zoom].keys():
                for tile_y in zoom_levels[zoom][tile_x].keys():
                    # Check if the tile has already been inserted
                    if zoom_levels[zoom][tile_x][tile_y]["already_inserted"]:
                        continue
                    new_representatives = []
                    for representative in zoom_levels[zoom][tile_x][tile_y]["representatives"]:
                        new_representative = {
                            "index": int(representative["representative"]["index"]),
                            "path": str(representative["representative"]["path"]),
                            "x": float(representative["representative"]["x"]),
                            "y": float(representative["representative"]["y"]),
                            "width": int(representative["representative"]["width"]),
                            "height": int(representative["representative"]["height"]),
                            "zoom": int(images_to_tile[representative["representative"]["index"]][0])
                        }
                        new_representatives.append(new_representative)

                    # Create entity
                    entity = {
                        "index": get_index_from_tile(zoom, tile_x, tile_y),
                        ZOOM_LEVEL_VECTOR_FIELD_NAME: [zoom, tile_x, tile_y],
                        "data": new_representatives
                    }

                    if zoom == 0:
                        entity["range"] = {
                            "x_min": float(zoom_levels[zoom][tile_x][tile_y]["range"]["x_min"]),
                            "x_max": float(zoom_levels[zoom][tile_x][tile_y]["range"]["x_max"]),
                            "y_min": float(zoom_levels[zoom][tile_x][tile_y]["range"]["y_min"]),
                            "y_max": float(zoom_levels[zoom][tile_x][tile_y]["range"]["y_max"])
                        }

                    # Insert entity
                    entities_to_insert.append(entity)
                    # Mark as inserted
                    zoom_levels[zoom][tile_x][tile_y]["already_inserted"] = True

        # Insert entities in the collection
        for i in range(0, len(entities_to_insert), INSERT_SIZE):
            collection.insert(data=entities_to_insert[i:i + INSERT_SIZE])

        # Flush collection
        collection.flush()

    except Exception as e:
        print("Error in insert_vectors_in_clusters_collection. Error message: ", e)
        return False

    if last_call:
        return True

    # FREE UP ZOOM LEVELS DICTIONARY. KEEP AT MOST LIMIT_FOR_KEEP ENTITIES FROM THE LAST TWO ZOOM LEVELS.
    assert max(zoom_levels.keys()) == zoom_level
    # Compute the tile at the previous zoom which corresponds to the current tile
    prev_x = current_tile_x // 2
    prev_y = current_tile_y // 2
    # Get keys of zoom_levels in order
    zoom_levels_keys = sorted(list(zoom_levels.keys()))
    for zoom in zoom_levels_keys:
        if zoom < zoom_level - 1:
            del zoom_levels[zoom]
            entities_per_zoom_level[zoom] = 0
        else:
            if zoom == zoom_level - 1:
                # Get keys of tile_x in order
                tile_x_keys = sorted(list(zoom_levels[zoom].keys()))
                for tile_x in tile_x_keys:
                    if tile_x < prev_x:
                        entities_per_zoom_level[zoom] -= len(zoom_levels[zoom][tile_x].keys())
                        del zoom_levels[zoom][tile_x]
                    elif tile_x == prev_x:
                        tile_y_keys = sorted(list(zoom_levels[zoom][tile_x].keys()))
                        for tile_y in tile_y_keys:
                            if tile_y < prev_y:
                                entities_per_zoom_level[zoom] -= 1
                                del zoom_levels[zoom][tile_x][tile_y]
                            else:
                                break
                    else:
                        break
            else:
                # Remove tiles from current zoom level until we have at most LIMIT_FOR_KEEP entities
                if entities_per_zoom_level[zoom] <= LIMIT_FOR_KEEP - entities_per_zoom_level[zoom - 1]:
                    break
                # Get keys of tile_x in order
                tile_x_keys = sorted(list(zoom_levels[zoom].keys()))
                for tile_x in tile_x_keys:
                    entities_per_zoom_level[zoom] -= len(zoom_levels[zoom][tile_x].keys())
                    del zoom_levels[zoom][tile_x]
                    if (entities_per_zoom_level[zoom] <= LIMIT_FOR_KEEP
                            - entities_per_zoom_level[zoom - 1]):
                        break

    # If the number of entities kept is still greater than LIMIT_FOR_KEEP, then remove entities from the second to
    # last zoom level until we have at most LIMIT_FOR_KEEP entities
    if entities_per_zoom_level[zoom_level - 1] > LIMIT_FOR_KEEP:
        # Get keys of tile_x in order
        tile_x_keys = sorted(list(zoom_levels[zoom_level - 1].keys()), reverse=True)
        for tile_x in tile_x_keys:
            entities_per_zoom_level[zoom_level - 1] -= len(zoom_levels[zoom_level - 1][tile_x].keys())
            del zoom_levels[zoom_level - 1][tile_x]
            if entities_per_zoom_level[zoom_level - 1] <= LIMIT_FOR_KEEP:
                break

    return True


def get_previously_inserted_tile(collection: Collection, prev_zoom_level: int, prev_tile_x: int, prev_tile_y: int,
                                 zoom_levels: dict, entities_per_zoom_level: dict) -> bool:
    # Get LIMIT_FOR_FETCH tiles
    # Loop over tiles in the previous zoom level, and add index of tile if the tile is not in zoom_levels
    indexes = []
    for tile_x in range(prev_tile_x, 2 ** prev_zoom_level):
        for tile_y in range(prev_tile_y, 2 ** prev_zoom_level):
            if (prev_zoom_level in zoom_levels.keys() and tile_x in zoom_levels[prev_zoom_level].keys()
                    and tile_y in zoom_levels[prev_zoom_level][tile_x].keys()):
                continue
            indexes.append(get_index_from_tile(prev_zoom_level, tile_x, tile_y))
            if len(indexes) == LIMIT_FOR_FETCH:
                break

    # Get previously inserted tile
    try:
        for i in range(0, len(indexes), SEARCH_LIMIT):
            entities = collection.query(
                expr=f"index in {indexes[i:i + SEARCH_LIMIT]}",
                output_fields=[ZOOM_LEVEL_VECTOR_FIELD_NAME, "data"]
            )
            # Add entities to zoom_levels. Use original format with representatives
            for entity in entities:
                tile = entity[ZOOM_LEVEL_VECTOR_FIELD_NAME]
                data = entity["data"]
                if prev_zoom_level not in zoom_levels.keys():
                    zoom_levels[prev_zoom_level] = {}
                if int(tile[1]) not in zoom_levels[prev_zoom_level].keys():
                    zoom_levels[prev_zoom_level][int(tile[1])] = {}
                zoom_levels[prev_zoom_level][int(tile[1])][int(tile[2])] = {
                    "already_inserted": True,
                    "representatives": [{"representative": representative} for representative in data]
                }
                entities_per_zoom_level[prev_zoom_level] += 1

        return True

    except Exception as e:
        print("Error in get_previously_inserted_tile. Error message: ", e)
        return False


def create_image_to_tile_collection(images_to_tile: dict, zoom_levels_collection_name: str,
                                    images_to_tile_collection_name: str):
    # Create collection and index
    collection = image_to_tile_collection(images_to_tile_collection_name)

    # Populate collection
    entities_to_insert = []
    for index in images_to_tile.keys():
        assert len(images_to_tile[index]) == 3 and isinstance(index, int)
        # Create entity
        entity = {
            "index": index,
            ZOOM_LEVEL_VECTOR_FIELD_NAME: images_to_tile[index]
        }
        # Insert entity
        entities_to_insert.append(entity)

    # Insert entities in the collection
    try:
        for i in range(0, len(entities_to_insert), INSERT_SIZE):
            collection.insert(data=entities_to_insert[i:i + INSERT_SIZE])
        # Flush collection
        collection.flush()
    except Exception as e:
        graceful_application_shutdown(
            f"Error in create_image_to_tile_collection. Error message: {e}",
            zoom_levels_collection_name,
            images_to_tile_collection_name
        )


def create_tiling(entities) -> tuple[list[list[list[dict]]], int]:
    # Randomly shuffle the entities.
    np.random.shuffle(entities)

    # Find the maximum and minimum values for each dimension
    max_values = {"x": max([entity["x"] for entity in entities]), "y": max([entity["y"] for entity in entities])}
    min_values = {"x": min([entity["x"] for entity in entities]), "y": min([entity["y"] for entity in entities])}

    # Find zoom level that allows to have tiles with at most MAX_IMAGES_PER_TILE images.
    max_zoom_level = 0
    while True:
        # Define grid for entire embeddings space.
        number_of_tiles = 2 ** max_zoom_level
        grid = [[[] for _ in range(number_of_tiles)] for _ in range(number_of_tiles)]

        # Associate each entity to a tile.
        for entity in entities:
            # Shift the values by the minimum value of both dimensions so that the minimum value is 0
            x = entity["x"] - min_values["x"]
            y = entity["y"] - min_values["y"]

            # Find the tile to which the entity belongs.
            tile_x = min(int((x * number_of_tiles) // (max_values["x"] - min_values["x"])),
                         number_of_tiles - 1)
            tile_y = min(int((y * number_of_tiles) // (max_values["y"] - min_values["y"])),
                         number_of_tiles - 1)

            # Add entity to the tile
            grid[tile_x][tile_y].append(entity)

        # Check if the number of images in each tile is less than MAX_IMAGES_PER_TILE
        max_images_per_tile = 0
        tot_images = 0
        for row in grid:
            for tile in row:
                if len(tile) > max_images_per_tile:
                    max_images_per_tile = len(tile)
                tot_images += len(tile)

        assert tot_images == len(entities)

        if max_images_per_tile <= MAX_IMAGES_PER_TILE:
            break
        else:
            max_zoom_level += 1

    # Return grid
    return grid, max_zoom_level


def graceful_application_shutdown(message: str, zoom_levels_collection_name: str, images_to_tile_collection_name: str):
    print(message)
    # Drop collections
    if utility.has_collection(zoom_levels_collection_name):
        utility.drop_collection(zoom_levels_collection_name)
    if utility.has_collection(images_to_tile_collection_name):
        utility.drop_collection(images_to_tile_collection_name)
    sys.exit(1)


def create_zoom_levels(entities, zoom_levels_collection_name, images_to_tile_collection_name):
    # Take entire embedding space for zoom level 0, then divide each dimension into 2^zoom_levels intervals.
    # Each interval is a tile. For each tile, find clusters and cluster representatives. Keep track of
    # the number of entities in each cluster. For the last zoom level, show all the entities in each tile.
    # First, get tiling
    tiling, max_zoom_level = create_tiling(entities)

    # Save max_zoom_level to the entry in datasets.json
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "r") as f:
        datasets = json.load(f)["datasets"]
        for dataset in datasets:
            if dataset["name"] == zoom_levels_collection_name.removesuffix("_zoom_levels_clusters"):
                dataset["zoom_levels"] = max_zoom_level
                break
    with open(os.path.join(os.getenv(HOME), DATASETS_JSON_NAME), "w") as f:
        json.dump({"datasets": datasets}, f, indent=4)

    # Create clusters collection
    zoom_levels_collection = clusters_collection(zoom_levels_collection_name)

    # Define dictionary for zoom levels
    zoom_levels = {}
    # Define dictionary for number of entities in zoom level
    entities_per_zoom_level = {}
    # Define dictionary for mapping from images to coarser zoom level (and tile)
    images_to_tile = {}

    # Load the collection of zoom levels
    zoom_levels_collection.load()

    for zoom_level in tqdm(range(0, max_zoom_level + 1), desc="Zoom level", position=0):
        zoom_levels[zoom_level] = {}
        entities_per_zoom_level[zoom_level] = 0
        # First tile goes from 0 to 2 ** (max_zoom_level - zoom_level) - 1, second tile goes from
        # 2 ** (max_zoom_level - zoom_level) to 2 ** (max_zoom_level - zoom_level) * 2 - 1, and so on.
        for tile_x in tqdm(range(0, 2 ** max_zoom_level, 2 ** (max_zoom_level - zoom_level)), desc="Tile x",
                           position=1, leave=False):
            # Get index of tile along x-axis
            tile_x_index = int(tile_x // 2 ** (max_zoom_level - zoom_level))
            zoom_levels[zoom_level][tile_x_index] = {}

            for tile_y in tqdm(range(0, 2 ** max_zoom_level, 2 ** (max_zoom_level - zoom_level)), desc="Tile y",
                               position=2, leave=False):
                # Get index of tile along y-axis
                tile_y_index = int(tile_y // 2 ** (max_zoom_level - zoom_level))
                # Flush if necessary
                if sum([entities_per_zoom_level[zoom] for zoom in entities_per_zoom_level.keys()]) >= LIMIT_FOR_TOTAL:
                    # Insert data in collection
                    result = insert_vectors_in_clusters_collection(
                        zoom_levels, images_to_tile, zoom_levels_collection, entities_per_zoom_level,
                        zoom_level, tile_x_index, tile_y_index
                    )
                    if result:
                        # Adjust zoom_levels dictionary
                        zoom_levels[zoom_level] = {}
                        if tile_x_index not in zoom_levels[zoom_level].keys():
                            zoom_levels[zoom_level][tile_x_index] = {}
                    else:
                        # Shut down application
                        graceful_application_shutdown(
                            "Could not insert data in collection.",
                            zoom_levels_collection_name,
                            images_to_tile_collection_name
                        )

                # Get all entities in the current tile.
                entities_in_tile = []
                count = 0
                for x in range(tile_x, tile_x + 2 ** (max_zoom_level - zoom_level)):
                    for y in range(tile_y, tile_y + 2 ** (max_zoom_level - zoom_level)):
                        # Get all entities in the tile
                        entities_in_tile += tiling[x][y]
                        count += 1

                assert count == 4 ** (max_zoom_level - zoom_level)

                # Get cluster representatives that where selected in the previous zoom level and are in the current
                # tile.
                # First, get index of tile from the previous zoom level which contains the current tile
                prev_level_x = int(tile_x_index // 2)
                prev_level_y = int(tile_y_index // 2)

                # Get cluster representatives from previous zoom level
                old_cluster_representatives_in_current_tile = []
                if zoom_level != 0:
                    if not (zoom_level - 1 in zoom_levels and prev_level_x in zoom_levels[zoom_level - 1].keys()
                            and prev_level_y in zoom_levels[zoom_level - 1][prev_level_x].keys()):
                        # Get cluster representatives from the collection
                        result = get_previously_inserted_tile(
                            zoom_levels_collection, zoom_level - 1, prev_level_x, prev_level_y, zoom_levels,
                            entities_per_zoom_level
                        )
                        if not result:
                            # Shut down application
                            graceful_application_shutdown(
                                "Could not get previously inserted tile.",
                                zoom_levels_collection_name,
                                images_to_tile_collection_name
                            )

                    previous_zoom_level_cluster_representatives = [representative["representative"] for
                                                                   representative in zoom_levels[zoom_level - 1]
                                                                   [prev_level_x][prev_level_y]["representatives"]]

                    # Get cluster representatives that are in the current tile.
                    # old_cluster_representatives_in_current_tile must be cluster representatives in the current tile.
                    for representative in previous_zoom_level_cluster_representatives:
                        for entity in entities_in_tile:
                            if entity["index"] == representative["index"]:
                                old_cluster_representatives_in_current_tile.append(representative)
                                break

                # Define vector of representative entities
                representative_entities = []
                # Check if there are less than MAX_IMAGES_PER_TILE images in the tile.
                if len(entities_in_tile) <= MAX_IMAGES_PER_TILE:
                    for entity in entities_in_tile:
                        # Check if the entity is in the previous zoom level
                        in_previous = False
                        for old_rep in old_cluster_representatives_in_current_tile:
                            if entity["index"] == old_rep["index"]:
                                in_previous = True
                                break
                        representative_entities.append(
                            {
                                "representative": entity,
                                "number_of_entities": 0,
                                "in_previous": in_previous
                            }
                        )

                    # Check if all the elements in old_cluster_representatives_in_current_tile have in_previous
                    # set to True.
                    indexes = [old_rep["index"] for old_rep in old_cluster_representatives_in_current_tile]
                    count = 0
                    for rep in representative_entities:
                        if rep["representative"]["index"] in indexes:
                            count += 1
                            assert rep["in_previous"]
                        else:
                            assert not rep["in_previous"]
                    assert count == len(old_cluster_representatives_in_current_tile)

                    assert (sum([cluster["number_of_entities"] + 1 for cluster in representative_entities])
                            == len(entities_in_tile))

                else:
                    # Get the coordinates of the entities in the tile
                    coordinates = np.array([[entity["x"], entity["y"]] for entity in entities_in_tile])

                    # Perform clustering
                    kmeans = ModifiedKMeans(n_clusters=NUMBER_OF_CLUSTERS, random_state=0, n_init=1, max_iter=1000)

                    if len(old_cluster_representatives_in_current_tile) > 0:
                        fixed_centers = np.array([[entity["x"], entity["y"]] for entity in
                                                  old_cluster_representatives_in_current_tile])
                    else:
                        fixed_centers = None

                    try:
                        kmeans.fit(coordinates, fixed_centers=fixed_centers)
                    except Exception as e:
                        graceful_application_shutdown(
                            f"Error in kmeans.fit. Error message: {e}",
                            zoom_levels_collection_name,
                            images_to_tile_collection_name
                        )

                    # Get the coordinates of the cluster representatives
                    cluster_representatives = kmeans.cluster_centers_

                    # Assert that the number of cluster representatives is equal to NUMBER_OF_CLUSTERS
                    assert len(cluster_representatives) == NUMBER_OF_CLUSTERS

                    # Check that the first len(old_cluster_representatives_in_current_tile) cluster_representatives are
                    # the same as the old_cluster_representatives_in_current_tile
                    for i in range(len(old_cluster_representatives_in_current_tile)):
                        assert (old_cluster_representatives_in_current_tile[i]["x"] == cluster_representatives[i][0])
                        assert (old_cluster_representatives_in_current_tile[i]["y"] == cluster_representatives[i][1])

                    # Find the entity closest to the centroid of each cluster
                    temp_cluster_representatives_entities = []
                    num_entities = 0
                    for cluster in range(NUMBER_OF_CLUSTERS):
                        # Get the entities in the cluster
                        entities_in_cluster = [entity for entity in entities_in_tile
                                               if kmeans.predict(np.array([[entity["x"], entity["y"]]]))[0] == cluster]
                        num_entities += len(entities_in_cluster)

                        if cluster < len(old_cluster_representatives_in_current_tile):
                            # Add old cluster representative to temp_cluster_representatives_entities
                            temp_cluster_representatives_entities.append(
                                {
                                    "representative": old_cluster_representatives_in_current_tile[cluster],
                                    "number_of_entities": len(entities_in_cluster) - 1,
                                    "in_previous": True
                                }
                            )

                        else:
                            # Get the entity closest to the centroid of the cluster
                            def l2(entity):
                                return ((entity["x"] - cluster_representatives[cluster][0]) ** 2
                                        + (entity["y"] - cluster_representatives[cluster][1]) ** 2)

                            temp_cluster_representatives_entities.append(
                                {
                                    "representative": min(entities_in_cluster, key=l2),
                                    "number_of_entities": len(entities_in_cluster) - 1,
                                    "in_previous": False
                                }
                            )

                    assert num_entities == len(entities_in_tile)

                    representative_entities = temp_cluster_representatives_entities

                    # Check if the all the element in old_cluster_representatives_in_current_tile have in_previous
                    # set to True.
                    indexes = [old_rep["index"] for old_rep in old_cluster_representatives_in_current_tile]
                    count = 0
                    for rep in representative_entities:
                        if rep["representative"]["index"] in indexes:
                            count += 1
                            assert rep["in_previous"]
                        else:
                            assert not rep["in_previous"]

                    assert count == len(old_cluster_representatives_in_current_tile)

                    assert (sum([cluster["number_of_entities"] + 1 for cluster in representative_entities])
                            == len(entities_in_tile))

                # Save information for tile in zoom_levels. Cluster representatives are the entities themselves.
                zoom_levels[zoom_level][tile_x_index][tile_y_index] = {}
                zoom_levels[zoom_level][tile_x_index][tile_y_index]["representatives"] = representative_entities
                zoom_levels[zoom_level][tile_x_index][tile_y_index]["already_inserted"] = False
                entities_per_zoom_level[zoom_level] += 1

                if zoom_level == 0:
                    zoom_levels[zoom_level][tile_x_index][tile_y_index]["range"] = {
                        "x_min": min([entity["x"] for entity in entities_in_tile]),
                        "x_max": max([entity["x"] for entity in entities_in_tile]),
                        "y_min": min([entity["y"] for entity in entities_in_tile]),
                        "y_max": max([entity["y"] for entity in entities_in_tile])
                    }

                # Save mapping from images to tile
                for representative in representative_entities:
                    if representative["representative"]["index"] not in images_to_tile:
                        images_to_tile[representative["representative"]["index"]] = [
                            zoom_level, tile_x_index, tile_y_index
                        ]

    # Do a final insert in the collection
    result = insert_vectors_in_clusters_collection(
        zoom_levels, images_to_tile, zoom_levels_collection, entities_per_zoom_level, -1, -1, -1, True
    )
    if not result:
        # Shut down application
        graceful_application_shutdown(
            "Could not insert data in collection.",
            zoom_levels_collection_name,
            images_to_tile_collection_name
        )

    zoom_levels_collection.release()
    create_image_to_tile_collection(images_to_tile, zoom_levels_collection_name, images_to_tile_collection_name)


def check_if_collection_exists(collection_name: str, repopulate: bool):
    if utility.has_collection(collection_name) and (repopulate or Collection(collection_name).num_entities == 0):
        utility.drop_collection(collection_name)
    elif utility.has_collection(collection_name) and not (repopulate or Collection(collection_name).num_entities == 0):
        print(f"Found collection {collection_name}. It has more than 0 entities. Set repopulate to True to drop it.")
        sys.exit(0)


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

    # Define collection names
    zoom_levels_collection_name = flags["collection"] + "_zoom_levels_clusters"
    images_to_tile_collection_name = flags["collection"] + "_image_to_tile"
    # Check if collections exist
    check_if_collection_exists(zoom_levels_collection_name, flags["repopulate"])
    check_if_collection_exists(images_to_tile_collection_name, flags["repopulate"])

    # Check that embeddings collection exists. If the collection does not exist, return.
    if flags["collection"] not in utility.list_collections():
        print(f"The collection {flags['collection']}, which is needed for creating zoom levels, does not exist.")
        sys.exit(1)
    else:
        collection = Collection(flags["collection"])

    # Load vectors from collection
    entities = load_vectors_from_collection(collection)

    # Create zoom levels
    if entities is not None:
        create_zoom_levels(entities, zoom_levels_collection_name, images_to_tile_collection_name)
    else:
        print(f"No entities found in the collection {flags['collection']}.")
        sys.exit(1)
