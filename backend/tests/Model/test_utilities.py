import unittest

from backend.src.embeddings_model.utils import *


class TestEmbeddingsModel(unittest.TestCase):

    def test_project_embeddings_UMAP(self):
        with self.assertRaises(AssertionError):
            project_embeddings_UMAP(torch.randn(128))

        with self.assertRaises(AssertionError):
            project_embeddings_UMAP(torch.randn(100, 3), dim=3)

        projections = project_embeddings_UMAP(torch.randn(1000, 128), dim=2)
        self.assertTrue(projections.shape[0] == 1000 and projections.shape[1] == 2)
        self.assertIsInstance(projections, np.ndarray)
