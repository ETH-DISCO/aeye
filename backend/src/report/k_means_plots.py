import sys
import os

import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.metrics import euclidean_distances


class Plotter:
    def __init__(self, points_clusters):
        self.points_clusters = points_clusters
        self.labels = np.unique(points_clusters)

    def generate_scatter(self, points, centers, it):
        colors = ['pink', 'g', 'c', 'lightblue', 'y']
        for i in range(self.labels.shape[0]):
            # Find index of points that belong to the cluster
            indexes = np.where(self.points_clusters == i)
            cluster_points = points[indexes]
            plt.scatter(cluster_points[:, 0], cluster_points[:, 1], s=10, c=colors[i % len(colors)])

        plt.scatter(centers[:, 0], centers[:, 1], s=100, c='red', marker='x')
        # Create a directory to store the plots
        if not os.path.exists('kmeans_plots'):
            os.makedirs('kmeans_plots')
        # Save the plot
        plt.savefig(f'kmeans_plots/iteration_{it}.png')
        # Clear the plot
        plt.clf()


class KMeansWithPlots:
    def __init__(self, n_clusters, random_state, n_init=10, max_iter=300, plotter=None):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.n_init = n_init
        self.max_iter = max_iter
        self.plotter = plotter
        self._inertia = sys.maxsize
        self.cluster_centers_ = None

    @staticmethod
    def _compute_initial_centers(X, fixed_centers, num_remaining_centers, n_init):
        centroids = fixed_centers

        # compute remaining centroids
        for _ in range(num_remaining_centers):
            # initialize a list to store distances of data
            # points from nearest centroid
            dist = np.zeros(X.shape[0])
            for i in range(X.shape[0]):
                point = X[i, :]
                d = sys.maxsize

                # compute distance of 'point' from each of the previously
                # selected centroid and store the minimum distance
                for j in range(len(centroids)):
                    temp_dist = np.sum((point - centroids[j]) ** 2)
                    d = min(d, temp_dist)
                dist[i] = d

            # select data point with maximum distance as our next centroid
            if n_init == 1:
                next_centroid = X[np.argmax(dist), :]
            else:
                # Get centroid at random using probability proportional to distance
                next_centroid = X[np.random.choice(X.shape[0], p=dist / np.sum(dist)), :]

            if centroids.size == 0:
                centroids = next_centroid
            else:
                centroids = np.vstack([centroids, next_centroid])

        return centroids

    def fit(self, X, fixed_centers=None, initial_centers=None):
        # Do k-means clustering with fixed centers for self.n_init times. Keep the best result.
        if fixed_centers is None:
            fixed_centers = np.array([])
        for _ in range(self.n_init):
            # Generate random centers for the remaining clusters
            if initial_centers is not None:
                centers = initial_centers
            else:
                centers = KMeansWithPlots._compute_initial_centers(
                    X, fixed_centers, self.n_clusters - len(fixed_centers), self.n_init
                )
            # Plot the initial centers
            self.plotter.generate_scatter(X, centers, 0)
            # Do k-means clustering
            it = 0
            while it < self.max_iter:
                # Assign labels to each datapoint based on centers
                labels = np.argmin(euclidean_distances(X, centers), axis=1)
                # Find new centers from means of datapoints
                new_moving_centers = np.zeros((centers.shape[0] - fixed_centers.shape[0], X.shape[1]))
                for i in range(fixed_centers.shape[0], centers.shape[0]):
                    if i not in labels:
                        # If a cluster has no points, then set the center to a random point
                        new_moving_centers[i - fixed_centers.shape[0]] = X[np.random.choice(X.shape[0]), :]
                    else:
                        new_moving_centers[i - fixed_centers.shape[0]] = np.mean(X[labels == i], axis=0)
                # If centers have converged, then break
                if np.all(centers[fixed_centers.shape[0]:] == new_moving_centers):
                    break
                else:
                    centers[fixed_centers.shape[0]:] = new_moving_centers

                if it < 9:
                    self.plotter.generate_scatter(X, centers, it + 1)
                it += 1

            # Compute inertia and select the new result as best if it has lower inertia.
            inertia = np.sum(np.min(euclidean_distances(X, centers), axis=1))
            if inertia < self._inertia and inertia != 0:
                self._inertia = inertia
                self.cluster_centers_ = centers


if __name__ == '__main__':
    # Generate blobs for testing
    X, y = make_blobs(n_samples=1000, centers=5, n_features=2, random_state=42)
    # Create plotter
    plotter = Plotter(y)
    # Initialize KMeansWithPlots
    kmeans = KMeansWithPlots(n_clusters=5, random_state=42, n_init=1, max_iter=300, plotter=plotter)
    # Define initial centers
    centers = np.array([[-10, 5], [-10, -9], [-5, 10], [0, 2], [2.5, 2]])
    # Fit the model
    kmeans.fit(X, initial_centers=centers)
