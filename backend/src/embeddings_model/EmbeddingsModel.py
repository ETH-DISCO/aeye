import typing
from abc import ABC, abstractmethod

import numpy as np
import torch


class EmbeddingsModel(ABC):

    @abstractmethod
    def getSimilarityScore(self, emb1: torch.Tensor | np.ndarray, emb2: torch.Tensor | np.ndarray) \
            -> torch.Tensor | np.ndarray:
        """
        Return the similarity score between the two _embeddings of the same dimension.
        :param emb1: First vector of _embeddings.
        :param emb2: Second vector of _embeddings.
        :return: Similarity score between the two _embeddings.
        """
        pass

    @abstractmethod
    def getTextEmbeddings(self, text: str | typing.List[str]) -> torch.Tensor | np.ndarray:
        """
        Return textual embedding of a text.
        :param text: Text to embed.
        :return: Embeddings for text.
        """
        pass

    @abstractmethod
    def getImageEmbeddings(self, image) -> torch.Tensor | np.ndarray:
        """
        Return image embedding of an image.
        :param image: Image to embed.
        :return: Embeddings for image.
        """
        pass

    @abstractmethod
    def processData(self, data):
        """
        Return the inputs to the embeddings_model which generates the encodings.
        :param data:
        :return:
        """
        pass

    @abstractmethod
    def getEmbeddings(self, inputs) -> torch.Tensor | np.ndarray:
        """
        Return embedding of data. The type of data depends on the implementation.
        :param inputs: Inputs to the embeddings_model which generates the embeddings.
        :return: Embeddings for data.
        """
        pass
