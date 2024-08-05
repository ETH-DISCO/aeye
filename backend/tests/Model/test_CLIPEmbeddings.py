import unittest

import torch

from backend.src.embeddings_model.CLIPEmbeddings import ClipEmbeddings
from backend.src.embeddings_model.EmbeddingsModel import EmbeddingsModel


class TestCLIPEmbeddings(unittest.TestCase):

    def test_CLIPEmbeddings_instance_of_EmbeddingsModel(self):
        clip = ClipEmbeddings("cpu")
        self.assertIsInstance(clip, EmbeddingsModel)

    def test_shape_text_embeddings(self):
        clip = ClipEmbeddings("cpu")
        text = "test shape _embeddings"
        self.assertEqual((1, 512), clip.getTextEmbeddings(text).shape)

    def test_shape_image_embeddings(self):
        clip = ClipEmbeddings("cpu")
        img = torch.rand(3, 224, 224)
        self.assertEqual((1, 512), clip.getEmbeddings(clip.processData(img)).shape)

    def test_get_similarity_score(self):
        clip = ClipEmbeddings("cpu")

        with self.assertRaises(AssertionError):
            clip.getSimilarityScore(torch.randn(100, 128), torch.randn(100, 126))

        # Generate random image
        img = torch.rand(3, 224, 224)
        img_embeddings = clip.getEmbeddings(clip.processData(img))

        text = "test shape _embeddings"
        text_embeddings = clip.getTextEmbeddings(text)

        score = clip.getSimilarityScore(img_embeddings, text_embeddings)

        self.assertTrue(0 <= score.item() <= 1)
