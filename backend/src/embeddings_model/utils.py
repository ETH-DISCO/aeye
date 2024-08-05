import warnings

import numpy as np
import torch
from umap import UMAP

from ..CONSTANTS import *


def project_embeddings_UMAP(embeddings: torch.Tensor | np.ndarray, n_neighbors=DEFAULT_N_NEIGHBORS, dim=DEFAULT_DIM,
                            min_dist=DEFAULT_MIN_DIST) -> np.ndarray:
    """
    Project _embeddings onto lower dimensional space of dimension dim using UMAP_PROJ algorithm.
    :param embeddings: Embeddings of shape (NUM_EMBEDDINGS, EMBEDDINGS_DIM).
    :param n_neighbors: Number of the nearest neighbors used by the algorithm.
    :param dim: Dimensionality of projection space.
    :param min_dist: Minimum distance allowed between projected points.
    :return: Projected _embeddings.
    """
    assert len(embeddings.shape) == 2 and dim < embeddings.shape[1]

    # Project data
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        reducer = UMAP(n_neighbors=n_neighbors, n_components=dim, min_dist=min_dist, random_state=RANDOM_STATE,
                       n_jobs=1)
        return reducer.fit_transform(embeddings)
