import sys
from typing import Dict

import numpy as np
import torch
from tqdm import tqdm

from ..CONSTANTS import *
from ..embeddings_model.EmbeddingsModel import EmbeddingsModel
from ..embeddings_model.utils import project_embeddings_UMAP


class DatasetPreprocessor:
    """
    Module for generating the data which is stored in the database.
    """

    def __init__(self, embeddings_model: EmbeddingsModel):
        """
        :param embeddings_model: EmbeddingsModel object
        """
        self.embeddings_model = embeddings_model
        self._embeddings = None
        self._attributes = {}
        self._low_dim_embeddings = None

    def setEmbeddings(self, embeddings):
        self._embeddings = embeddings

    def _generateEmbeddings(self, inputs):
        """
        Generate _embeddings of data using the provided _embeddings embeddings_model. The method requires the inputs
        to the data encoder.
        """
        # This code works for dataloader with batch_size == 1
        if self._embeddings is None:
            self._embeddings = self.embeddings_model.getEmbeddings(inputs).detach()
        else:
            self._embeddings = torch.cat((self._embeddings,
                                          self.embeddings_model.getEmbeddings(inputs)), dim=0).detach()

    def _storeAttributes(self, data, attribute):
        if attribute not in self._attributes:
            self._attributes[attribute] = data[attribute]
        else:
            self._attributes[attribute] = self._attributes[attribute] + data[attribute]

    def _generateLowDimensionalEmbeddings(self, projection_method):
        try:
            assert self._embeddings is not None
            if projection_method == UMAP_PROJ:
                self._low_dim_embeddings = project_embeddings_UMAP(self._embeddings)
            else:
                raise Exception("Unknown projection method.")
        except Exception as e:
            print("Error in _generateLowDimensionalEmbeddings. Error: ", e)
            sys.exit(1)

    def generateRecordsMetadata(self, projection_method=DEFAULT_PROJECTION_METHOD) -> Dict[str, np.ndarray]:
        # Generate low dimensional embeddings
        self._generateLowDimensionalEmbeddings(projection_method)

        return {"low_dim_embeddings": self._low_dim_embeddings}

    def generateDatabaseEmbeddings(self, dataloader):
        """
        Generate dataset embeddings from the dataloader specified when creating the object. The method saves the
        indexes of the samples that could not be fetched in a file, with the index of the next sample after the last
        one that has been correctly fetched and processed.
        :param dataloader: dataloader object
        """
        try:
            for i, data in enumerate(tqdm(dataloader, desc="Processing", ncols=100,
                                          bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]")):
                if data is not None:
                    attributes = list(data.keys())
                    # Check if "index" is in attribute
                    if "index" not in attributes:
                        raise Exception("'index' must be present in each sample. Please modify the collate_fn "
                                        "function to include the attribute.")
                    # Generate data embeddings
                    self._generateEmbeddings(data[attributes[0]])
                    # Collect other attributes for the data points
                    if len(attributes) > 1:
                        for attribute in attributes[1:]:
                            self._storeAttributes(data, attribute)
                else:
                    print("Data is empty...moving on to next batch.")

            # Pack results in dictionary and return it to caller
            return {'embeddings': self._embeddings, **self._attributes}

        except Exception as e:
            # Print exception information
            print("Error in generateDatabaseEmbeddings. Error: ", e)
            sys.exit(1)
