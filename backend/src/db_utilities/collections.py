import numpy as np
from pymilvus import CollectionSchema, FieldSchema, DataType, Collection

from ..CONSTANTS import *

EMBEDDING_VECTOR_FIELD_NAME = "embedding"
ZOOM_LEVEL_VECTOR_FIELD_NAME = "tile"


def embeddings_collection(collection_name: str):
    # Create fields for collection
    index = FieldSchema(
        name="index",
        dtype=DataType.INT64,
        is_primary=True
    )
    x = FieldSchema(
        name="x",
        dtype=DataType.FLOAT,
        default_value=np.nan
    )
    y = FieldSchema(
        name="y",
        dtype=DataType.FLOAT,
        default_value=np.nan
    )
    embedding = FieldSchema(
        name=EMBEDDING_VECTOR_FIELD_NAME,
        dtype=DataType.FLOAT_VECTOR,
        dim=512
    )

    # Create collection schema
    schema = CollectionSchema(
        fields=[embedding, x, y, index],
        description="embeddings",
        enable_dynamic_field=True
    )

    # Create collection
    collection = Collection(
        name=collection_name,
        schema=schema,
        shards_num=1  # type: ignore
    )

    # Create index for embedding field to make similarity search faster
    index_params = {
        "metric_type": COSINE_METRIC,
        "index_type": INDEX_TYPE,
        "params": {}
    }

    collection.create_index(
        field_name="embedding",
        index_params=index_params
    )

    return collection


def clusters_collection(collection_name):
    """
    In the cluster collection, we save the following fields:
    - index: the index of the cluster
    - zoom_level: the zoom level of the cluster, with tile data information. Zoom level is a triplet
        (zoom_level, tile_x, tile_y).
    - data: the data of the cluster
    @param collection_name: the name of the collection    @return: the collection
    """
    # Create fields for collection
    index = FieldSchema(
        name="index",
        dtype=DataType.INT64,
        is_primary=True
    )
    tile = FieldSchema(
        name=ZOOM_LEVEL_VECTOR_FIELD_NAME,
        dtype=DataType.FLOAT_VECTOR,
        dim=3
    )
    data = FieldSchema(
        name="data",
        dtype=DataType.JSON
    )
    # Create collection schema
    schema = CollectionSchema(
        fields=[index, tile, data],
        description="zoom_levels_clusters",
        enable_dynamic_field=True
    )

    # Create collection
    collection = Collection(
        name=collection_name,
        schema=schema,
        shards_num=1  # type: ignore
    )

    index_params = {
        "metric_type": L2_METRIC,
        "index_type": INDEX_TYPE,
        "params": {}
    }

    collection.create_index(
        field_name=ZOOM_LEVEL_VECTOR_FIELD_NAME,
        index_params=index_params
    )

    return collection


def image_to_tile_collection(collection_name: str):
    # Create fields for collection
    index = FieldSchema(
        name="index",
        dtype=DataType.INT64,
        is_primary=True
    )
    tile = FieldSchema(
        name=ZOOM_LEVEL_VECTOR_FIELD_NAME,
        dtype=DataType.FLOAT_VECTOR,
        dim=3
    )

    # Create collection schema
    schema = CollectionSchema(
        fields=[index, tile],
        description="image_to_tile",
        enable_dynamic_field=True
    )

    # Create collection
    collection = Collection(
        name=collection_name,
        schema=schema,
        shards_num=1  # type: ignore
    )

    index_params = {
        "metric_type": L2_METRIC,
        "index_type": INDEX_TYPE,
        "params": {}
    }

    collection.create_index(
        field_name=ZOOM_LEVEL_VECTOR_FIELD_NAME,
        index_params=index_params
    )

    return collection


def umap_collection(collection_name: str, dim: int):
    # Create fields for collection
    index = FieldSchema(
        name="index",
        dtype=DataType.INT64,
        is_primary=True
    )
    n_neighbors = FieldSchema(
        name="n_neighbors",
        dtype=DataType.INT64
    )
    min_dist = FieldSchema(
        name="min_dist",
        dtype=DataType.FLOAT
    )
    data = FieldSchema(
        name="data",
        dtype=DataType.FLOAT_VECTOR,
        dim=dim * 2
    )

    # Create collection schema
    schema = CollectionSchema(
        fields=[index, n_neighbors, min_dist, data],
        description="umap",
        enable_dynamic_field=False
    )

    # Create collection
    collection = Collection(
        name=collection_name,
        schema=schema,
        shards_num=1  # type: ignore
    )

    index_params = {
        "metric_type": L2_METRIC,
        "index_type": INDEX_TYPE,
        "params": {}
    }

    collection.create_index(
        field_name="data",
        index_params=index_params
    )

    return collection
