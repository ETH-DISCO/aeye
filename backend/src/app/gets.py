import time
from typing import List

import torch
from pymilvus import Collection

from ..CONSTANTS import *
from ..db_utilities.collections import EMBEDDING_VECTOR_FIELD_NAME, ZOOM_LEVEL_VECTOR_FIELD_NAME


# Create decorator for timing functions
def timeit(func):
    """
    Decorator for timing functions.
    @param func:
    @return:
    """

    def wrapper(*args, **kwargs):
        """
        Wrapper for timing functions.
        @param args:
        @param kwargs:
        @return:
        """
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Function {func.__name__} took {(end - start) * 1000} milliseconds.")
        return result

    return wrapper


@timeit
def get_image_info_from_text_embedding(collection: Collection, text_embeddings: torch.Tensor) -> str:
    """
    Get the image embedding from the collection for a given text.
    @param collection:
    @param text_embeddings:
    @return:
    """
    # Define search parameters
    search_params = {
        "metric_type": COSINE_METRIC,
        "offset": 0
    }
    # Search image
    results = collection.search(
        data=text_embeddings.tolist(),
        anns_field=EMBEDDING_VECTOR_FIELD_NAME,
        param=search_params,
        limit=1,
        output_fields=["index", "author", "path", "width", "height", "genre", "date", "title", "caption", "x", "y"]
    )
    # Return image path
    return results[0][0].to_dict()["entity"]


@timeit
def get_tiles(indexes: List[int], collection: Collection) -> dict:
    """
    Get tiles from their indexes.
    @param indexes:
    @param collection:
    @return:
    """
    # Search image
    result = collection.query(
        expr=f"index in {indexes}",
        output_fields=["index", "data"]
    )
    # The returned data is a list of entities.

    return result


@timeit
def get_tile_from_image(index: int, collection: Collection) -> dict:
    """
    Get the tile data from the collection for a given image.
    @param index:
    @param collection:
    @return:
    """
    # Search image
    results = collection.query(
        expr=f"index in [{index}]",
        output_fields=["*"]
    )
    # The returned data point has the following format:
    # {
    #     "index": image_index,
    #     "zoom_plus_tile": [zoom_level, tile_x, tile_y]
    # }
    # Transform results[0][ZOOM_LEVEL_VECTOR_FIELD_NAME] to a list of integers
    if len(results) > 0:
        results[0][ZOOM_LEVEL_VECTOR_FIELD_NAME] = [int(x) for x in results[0][ZOOM_LEVEL_VECTOR_FIELD_NAME]]
        return results[0]
    else:
        return {}


@timeit
def get_paths_from_indexes(indexes: List[int], collection: Collection) -> dict:
    """
    Get images from their indexes.
    @param indexes:
    @param collection:
    @return:
    """
    # Search image
    results = collection.query(
        expr=f"index in {indexes}",
        output_fields=["path"]
    )

    # Return results
    return results


@timeit
def get_neighbors(index: int, collection: Collection, top_k: int) -> List[dict]:
    """
    Get the neighbors of a given image.
    @param index:
    @param collection:
    @param top_k:
    @return:
    """
    # First, query the index to find the embedding vector
    results = collection.query(
        expr=f"index in [{index}]",
        output_fields=[EMBEDDING_VECTOR_FIELD_NAME]
    )

    # Define search parameters
    search_params = {
        "metric_type": COSINE_METRIC
    }
    # Search image
    results = collection.search(
        data=[results[0][EMBEDDING_VECTOR_FIELD_NAME]],
        anns_field=EMBEDDING_VECTOR_FIELD_NAME,
        param=search_params,
        limit=top_k + 1,
        output_fields=["index", "author", "path", "width", "height", "genre", "date", "title", "caption", "x", "y"]
    )
    # Return results
    return [hit.to_dict()["entity"] for hit in results[0]]


@timeit
def get_first_tiles(collection: Collection) -> List[dict]:
    """
    Get tiles from first few zoom levels.
    @param collection:
    @return:
    """
    # Define limit on number of entities
    limit = min(collection.num_entities, 1365)
    results = []
    i = 0
    while i < limit:
        search_limit = min(16384, limit - i)
        # Search image
        results += collection.query(
            expr=f"index in {list(range(i, i + search_limit))}",
            output_fields=["index", "data", "range"],
            limit=search_limit
        )
        i += 16384

    # Return results
    return results


def get_umap_data(umap_c: Collection, n_neighbors: int, min_dist: float):
    """
    Get plot umap.
    @return:
    """
    # Check that n_neighbors and min_dist are among the allowed values
    if n_neighbors not in N_NEIGHBORS:
        raise ValueError(f"n_neighbors must be in {N_NEIGHBORS}")
    if min_dist not in MIN_DISTS:
        raise ValueError(f"min_dist must be in {MIN_DISTS}")
    # Get position of n_neighbors and min_dist in the allowed values
    n_neighbors_index = N_NEIGHBORS.index(n_neighbors)
    min_dist_index = MIN_DISTS.index(min_dist)
    # Compute index
    index = n_neighbors_index * len(MIN_DISTS) + min_dist_index

    # Load data for best artworks from the database
    results = umap_c.query(
        expr=f"index in [{index}]",
        output_fields=["data"]
    )

    x = [float(results[0]["data"][i]) for i in range(len(results[0]["data"])) if i % 2 == 0]
    y = [float(results[0]["data"][i]) for i in range(len(results[0]["data"])) if i % 2 == 1]

    # Return results
    return {"x": x, "y": y}


def get_random_image(num: float, collection: Collection) -> dict:
    """
    Get a random image from the collection.
    @param num:
    @param collection:
    @return:
    """
    # Get random index
    index = int(num * collection.num_entities)
    # Search image
    results = collection.query(
        expr=f"index in [{index}]",
        output_fields=["path", "caption"]
    )
    # Return results
    return results[0]


def get_image_info_from_image_embedding(collection: Collection, image_embeddings: torch.Tensor) -> dict:
    """
    Get the image from the collection for a given image embedding.
    @param collection:
    @param image_embeddings:
    @return:
    """
    # Define search parameters
    search_params = {
        "metric_type": COSINE_METRIC,
        "offset": 0
    }
    # Search image
    results = collection.search(
        data=image_embeddings.tolist(),
        anns_field=EMBEDDING_VECTOR_FIELD_NAME,
        param=search_params,
        limit=1,
        output_fields=["index", "author", "path", "width", "height", "genre", "date", "title", "caption", "x", "y"]
    )
    # Return image path
    return results[0][0].to_dict()["entity"]
