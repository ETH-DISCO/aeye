import json
import threading
from typing import List

import torch
from fastapi import Query
from pymilvus import Collection
from pymilvus.orm import utility

from .CONSTANTS import *
from ..CONSTANTS import UMAP_COLLECTION_NAME
from ..embeddings_model.EmbeddingsModel import EmbeddingsModel


# Define helper class for representing a collection
class HelperCollection:
    def __init__(self, name: str):
        self.name = name
        self.collection = Collection(name)
        self.load = self.collection.load
        self.release = self.collection.release
        # Define counter. The counter is initialized to 0. When the collection is queried for the first time,
        # it is loaded, and the counter is set to a value greater than 0. Every time the collection is not used by an
        # app1 method that accesses the database, the counter is decremented by 1. Once the counter becomes 0,
        # the collection is released. Every time the collection is queried, the counter is set to the value. It the
        # collection had been released, it is loaded again once queried.
        self.counter = 0
        # Create lock to ensure that the counter is not accessed by multiple threads at the same time.
        self.lock = threading.Lock()


class CollectionNameGetter:
    def __init__(self, datasets: List, suffix: str = ""):
        # Define lock for the collection name getter
        self.lock = threading.Lock()
        self.collections = {}
        # Get collections from DatasetOptions
        for dataset in datasets:
            name = dataset["name"] + suffix
            if name in utility.list_collections():
                self.collections[name] = HelperCollection(name)

    def __call__(self, collection: str = Query(...)) -> Collection | None:
        self.lock.acquire()
        try:
            value = self._call(collection)
        finally:
            self.lock.release()
        return value

    def _call(self, collection: str = Query(...)) -> Collection | None:
        pass

    def update_counters(self, collection_name: str):
        # Log all counters before updating them
        # print(f"Before update. Counters: {[(key, self.collections[key].counter) for key in self.collections.keys()]}")
        # Loop over collections. If the collection is not the one that was queried, decrement its counter. Else, if
        # the collection is the one that was queried, set its counter to COUNTER_MAX_VALUE.
        for key in self.collections.keys():
            self.collections[key].lock.acquire()
            if key != collection_name:
                if self.collections[key].counter == 1:
                    self.collections[key].release()
                self.collections[key].counter = max(0, self.collections[key].counter - 1)
            else:
                if self.collections[key].counter == 0:
                    self.collections[key].load()
                self.collections[key].counter = COUNTER_MAX_VALUE
            self.collections[key].lock.release()

        # Log all counters after updating them
        # print(f"After update. Counters: {[(key, self.collections[key].counter) for key in self.collections.keys()]}")


class DatasetCollectionNameGetter(CollectionNameGetter):
    def __init__(self, datasets: List):
        super().__init__(datasets)

    def _call(self, collection: str = Query(...)) -> Collection | None:
        if collection in self.collections.keys():
            # Update counter for all collections
            self.update_counters(collection)
            # Return the requested collection
            return self.collections[collection].collection
        else:
            return None


class ClustersCollectionNameGetter(CollectionNameGetter):
    def __init__(self, datasets: List):
        super().__init__(datasets, "_zoom_levels_clusters")

    def _call(self, collection: str = Query(...)) -> Collection | None:
        if collection in self.collections.keys():
            # Update counter for all collections
            self.update_counters(collection)
            # Return the requested collection
            return self.collections[collection].collection
        else:
            return None


class ImageToTileCollectionNameGetter(CollectionNameGetter):
    def __init__(self, datasets: List):
        super().__init__(datasets, "_image_to_tile")

    def _call(self, collection: str = Query(...)) -> Collection | None:
        if collection in self.collections.keys():
            # Update counter for all collections
            self.update_counters(collection)
            # Return the requested collection
            return self.collections[collection].collection
        else:
            return None


class UMAPCollectionGetter:
    def __init__(self):
        self.collection = Collection(UMAP_COLLECTION_NAME)
        # Load collection in memory
        self.collection.load()

    def __call__(self) -> Collection:
        return self.collection


class DatasetCollectionInfoGetter:
    def __init__(self, datasets: List):
        self.collections = {}
        # Get collections from datasets
        for dataset in datasets:
            name = dataset["name"]
            if name in utility.list_collections():
                self.collections[name] = {"number_of_entities": Collection(name).num_entities,
                                          "zoom_levels": dataset["zoom_levels"]}

    def __call__(self, collection: str = Query(...)):
        if collection in self.collections.keys():
            # Update info if necessary
            with open(DATASETS_JSON_PATH, "r") as f:
                datasets = json.load(f)["datasets"]
            for dataset in datasets:
                if dataset["name"] == collection:
                    self.collections[collection]["zoom_levels"] = dataset["zoom_levels"]
                    break

            return self.collections[collection]
        else:
            return None


class Updater:
    """
    Class for updating the collections. When the client requests the list of collections, it could become necessary to
    update the list of collections if a new collection has been created.
    """

    def __init__(self, dataset_collection_name_getter: DatasetCollectionNameGetter,
                 clusters_collection_name_getter: ClustersCollectionNameGetter,
                 image_to_tile_collection_name_getter: ImageToTileCollectionNameGetter):
        self.dataset_collection_name_getter = dataset_collection_name_getter
        self.clusters_collection_name_getter = clusters_collection_name_getter
        self.image_to_tile_collection_name_getter = image_to_tile_collection_name_getter
        # Define variable to store the list of datasets
        self.datasets = None
        # Define lock for the updater
        self.lock = threading.Lock()

    def __call__(self):
        print("Updater called")
        with open(DATASETS_JSON_PATH, "r") as f:
            self.datasets = json.load(f)["datasets"]

        # Acquire lock
        self.lock.acquire()
        try:
            # First, update the list of collections if necessary
            for dataset in self.datasets:
                name = dataset["name"]
                if (name in utility.list_collections() and
                        name not in self.dataset_collection_name_getter.collections.keys()):
                    # The collection is in the database, but not in the list of collections. Add it to the list.
                    self.dataset_collection_name_getter.collections[name] = HelperCollection(name)
            # Second, update the list of zoom level collections if necessary
            for dataset in self.datasets:
                name = dataset["name"] + "_zoom_levels_clusters"
                # Check if name is the suffix of one of the elements of the list of collections
                if (name in utility.list_collections() and
                        name not in self.clusters_collection_name_getter.collections.keys()):
                    # The collection is in the database, but not in the list of collections. Add it to the list.
                    self.clusters_collection_name_getter.collections[name] = HelperCollection(name)

                name = dataset["name"] + "_image_to_tile"
                # Check if name is the suffix of one of the elements of the list of collections
                if (name in utility.list_collections() and
                        name not in self.image_to_tile_collection_name_getter.collections.keys()):
                    # The collection is in the database, but not in the list of collections. Add it to the list.
                    self.image_to_tile_collection_name_getter.collections[name] = HelperCollection(name)

            # Now, return the list of collections
            return [{"name": dataset["name"], "website_name": dataset["website_name"]} for dataset in self.datasets
                    if dataset["name"] in utility.list_collections()]
        finally:
            # Release lock
            self.lock.release()


class Embedder:
    def __init__(self, embeddings: EmbeddingsModel):
        self.embeddings = embeddings

    def __call__(self, text: str = Query(...)) -> torch.Tensor:
        return self.embeddings.getTextEmbeddings(text)


def parse_comma_separated(indexes: str) -> List[int]:
    return [int(value) for value in indexes.split(',')]
