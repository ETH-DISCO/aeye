from abc import ABC

import torch
from transformers import CLIPProcessor, CLIPModel

from ..CONSTANTS import *
from .EmbeddingsModel import EmbeddingsModel


class ClipEmbeddings(EmbeddingsModel, ABC):
    def __init__(self, device):
        self.device = device
        self.model = CLIPModel.from_pretrained(CLIP_MODEL).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(CLIP_MODEL, )
        self.cosine_similarity = torch.nn.CosineSimilarity()

    def getSimilarityScore(self, emb1, emb2):
        """
        Return the cosine similarity between the two _embeddings.
        :param emb1: First embedding.
        :param emb2: Second embedding.
        :return: Cosine similarity.
        """
        assert emb1.shape == emb2.shape
        # Return cosine similarity between _embeddings
        return self.cosine_similarity(emb1, emb2)

    def getTextEmbeddings(self, text):
        try:
            # Get text inputs
            inputs = self.processor(text, padding=True, truncation=True, return_tensors="pt").to(self.device)
            # Return _embeddings
            return self.model.get_text_features(**inputs)
        except Exception as e:
            print(e.__str__())

    def getImageEmbeddings(self, image):
        try:
            # Get image inputs
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            # Return _embeddings
            return self.model.get_image_features(**inputs)
        except Exception as e:
            print(e.__str__())

    def processData(self, data):
        # Return inputs for CLIP embeddings_model
        try:
            return self.processor(images=data, return_tensors="pt").to(self.device)
        except Exception as e:
            print(e.__str__())

    def getEmbeddings(self, inputs):
        # Return _embeddings
        return self.model.get_image_features(**inputs)
