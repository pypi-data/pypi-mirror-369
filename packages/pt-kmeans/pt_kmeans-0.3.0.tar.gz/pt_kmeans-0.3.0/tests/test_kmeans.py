# pylint: disable=protected-access

import logging
import unittest

import torch

import pt_kmeans

logging.disable(logging.CRITICAL)


class TestKMeansInitialization(unittest.TestCase):
    def setUp(self) -> None:
        torch.manual_seed(0)
        self.x = torch.randn(100, 3)
        self.n_clusters = 5

    def test_initialization_shape(self) -> None:
        centers = pt_kmeans.initialize_centers(self.x, self.n_clusters, method="random")
        self.assertEqual(centers.shape, (self.n_clusters, self.x.shape[1]))

        centers = pt_kmeans.initialize_centers(self.x, self.n_clusters, method="kmeans++")
        self.assertEqual(centers.shape, (self.n_clusters, self.x.shape[1]))

    def test_kmeans_plus_plus_reproducibility(self) -> None:
        gen1 = torch.Generator().manual_seed(123)
        gen2 = torch.Generator().manual_seed(123)

        centers1 = pt_kmeans.initialize_centers(self.x, self.n_clusters, method="kmeans++", generator=gen1)
        centers2 = pt_kmeans.initialize_centers(self.x, self.n_clusters, method="kmeans++", generator=gen2)

        torch.testing.assert_close(centers1, centers2)

    def test_kmeans_plus_plus_with_chunking(self) -> None:
        centers_chunked = pt_kmeans.initialize_centers(self.x, self.n_clusters, method="kmeans++", chunk_size=10)
        self.assertEqual(centers_chunked.shape, (self.n_clusters, self.x.shape[1]))

        gen1 = torch.Generator().manual_seed(123)
        gen2 = torch.Generator().manual_seed(123)

        centers1_chunked = pt_kmeans.initialize_centers(
            self.x, self.n_clusters, method="kmeans++", generator=gen1, chunk_size=5
        )
        centers2_chunked = pt_kmeans.initialize_centers(
            self.x, self.n_clusters, method="kmeans++", generator=gen2, chunk_size=5
        )

        torch.testing.assert_close(centers1_chunked, centers2_chunked)

        # Compare with non-chunked to ensure consistency (though slight differences due to
        # random sampling in kmeans++ are possible in general, with fixed seed, it should be close)
        gen3 = torch.Generator().manual_seed(123)
        centers_non_chunked = pt_kmeans.initialize_centers(
            self.x, self.n_clusters, method="kmeans++", generator=gen3, chunk_size=None
        )
        torch.testing.assert_close(centers1_chunked, centers_non_chunked)


class TestDistanceComputation(unittest.TestCase):
    def setUp(self) -> None:
        self.x = torch.tensor([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        self.centers = torch.tensor([[1.0, 0.0], [0.0, 1.0]])

    def test_l2_distance_computation(self) -> None:
        distances = pt_kmeans._compute_distance(self.x, self.centers, distance_metric="l2")
        self.assertEqual(distances.shape, (3, 2))

        # First point [1,0] should have distance 0 to first center [1,0]
        self.assertAlmostEqual(distances[0, 0].item(), 0.0)

        # First point [1,0] should have distance 2 to second center [0,1]
        self.assertAlmostEqual(distances[0, 1].item(), 2.0, places=5)

    def test_l2_distance_computation_chunked_vs_full(self) -> None:
        large_x = torch.randn(1000, 50)
        large_centers = torch.randn(10, 50)

        distances_full = pt_kmeans._compute_distance(large_x, large_centers, distance_metric="l2", chunk_size=None)
        distances_chunked_small = pt_kmeans._compute_distance(
            large_x, large_centers, distance_metric="l2", chunk_size=100
        )
        distances_chunked_large = pt_kmeans._compute_distance(
            large_x, large_centers, distance_metric="l2", chunk_size=500
        )
        distances_chunked_one = pt_kmeans._compute_distance(large_x, large_centers, distance_metric="l2", chunk_size=1)

        # All chunked results should be identical to the full computation
        torch.testing.assert_close(distances_full, distances_chunked_small)
        torch.testing.assert_close(distances_full, distances_chunked_large)
        torch.testing.assert_close(distances_full, distances_chunked_one)

    def test_cosine_distance_computation(self) -> None:
        distances = pt_kmeans._compute_distance(self.x, self.centers, distance_metric="cosine")
        self.assertEqual(distances.shape, (3, 2))

        # First point [1,0] should have cosine distance 0 to first center [1,0]
        self.assertAlmostEqual(distances[0, 0].item(), 0.0)

        # First point [1,0] should have cosine distance 1 to second center [0,1]
        self.assertAlmostEqual(distances[0, 1].item(), 1.0, places=5)

    def test_compute_distance_l2_with_precomputed_x_squared_norm_chunked(self) -> None:
        x = torch.randn(100, 5)
        centers = torch.randn(3, 5)
        x_squared_norm = torch.sum(x**2, dim=1)

        distances_full = pt_kmeans._compute_distance(
            x, centers, distance_metric="l2", x_squared_norm=x_squared_norm, chunk_size=None
        )
        distances_chunked = pt_kmeans._compute_distance(
            x, centers, distance_metric="l2", x_squared_norm=x_squared_norm, chunk_size=10
        )

        torch.testing.assert_close(distances_full, distances_chunked)

    def test_cosine_distance_computation_chunked_vs_full(self) -> None:
        large_x = torch.randn(1000, 50)
        large_centers = torch.randn(10, 50)

        distances_full = pt_kmeans._compute_distance(large_x, large_centers, distance_metric="cosine", chunk_size=None)
        distances_chunked_small = pt_kmeans._compute_distance(
            large_x, large_centers, distance_metric="cosine", chunk_size=100
        )
        distances_chunked_large = pt_kmeans._compute_distance(
            large_x, large_centers, distance_metric="cosine", chunk_size=500
        )
        distances_chunked_one = pt_kmeans._compute_distance(
            large_x, large_centers, distance_metric="cosine", chunk_size=1
        )

        # All chunked results should be identical to the full computation
        torch.testing.assert_close(distances_full, distances_chunked_small)
        torch.testing.assert_close(distances_full, distances_chunked_large)
        torch.testing.assert_close(distances_full, distances_chunked_one)


class TestClusterAssignment(unittest.TestCase):
    def setUp(self) -> None:
        self.x = torch.tensor([[1.0, 1.0], [2.0, 2.0], [10.0, 10.0], [11.0, 11.0]])
        self.centers = torch.tensor([[1.5, 1.5], [10.5, 10.5]])

    def test_assign_clusters_shape(self) -> None:
        labels = pt_kmeans._assign_clusters(self.x, self.centers)
        self.assertEqual(labels.shape, (self.x.shape[0],))

    def test_assign_clusters_values(self) -> None:
        labels = pt_kmeans._assign_clusters(self.x, self.centers, distance_metric="l2")

        # Points [1,1] and [2,2] should be assigned to center [1.5,1.5] (index 0)
        # Points [10,10] and [11,11] should be assigned to center [10.5,10.5] (index 1)
        expected = torch.tensor([0, 0, 1, 1])
        torch.testing.assert_close(labels, expected)

    def test_assign_clusters_chunked(self) -> None:
        labels_full = pt_kmeans._assign_clusters(self.x, self.centers, chunk_size=None)
        labels_chunked = pt_kmeans._assign_clusters(self.x, self.centers, chunk_size=2)

        torch.testing.assert_close(labels_full, labels_chunked)


class TestCenterUpdate(unittest.TestCase):
    def setUp(self) -> None:
        self.x = torch.tensor([[1.0, 1.0], [2.0, 2.0], [10.0, 10.0], [11.0, 11.0]])
        self.labels = torch.tensor([0, 0, 1, 1])
        self.n_clusters = 2

    def test_update_centers_shape(self) -> None:
        new_centers = pt_kmeans._update_centers(self.x, self.labels, self.n_clusters)
        self.assertEqual(new_centers.shape, (self.n_clusters, self.x.shape[1]))

    def test_update_centers_values(self) -> None:
        new_centers = pt_kmeans._update_centers(self.x, self.labels, self.n_clusters)

        # Center 0 should be mean of [1,1] and [2,2] = [1.5, 1.5]
        # Center 1 should be mean of [10,10] and [11,11] = [10.5, 10.5]
        expected = torch.tensor([[1.5, 1.5], [10.5, 10.5]])

        torch.testing.assert_close(new_centers, expected)

    def test_empty_cluster_handling(self) -> None:
        # Create labels where cluster 1 is empty
        labels_with_empty = torch.tensor([0, 0, 0, 0])

        # This should not crash and should reinitialize the empty cluster
        new_centers = pt_kmeans._update_centers(self.x, labels_with_empty, self.n_clusters)
        self.assertEqual(new_centers.shape, (self.n_clusters, self.x.shape[1]))

        # First center should be mean of all points
        expected_center_0 = self.x.mean(dim=0)
        torch.testing.assert_close(new_centers[0], expected_center_0)


class TestKMeansFullAlgorithm(unittest.TestCase):
    def setUp(self) -> None:
        torch.manual_seed(0)
        cluster1 = torch.randn(30, 2) + torch.tensor([0.0, 0.0])
        cluster2 = torch.randn(30, 2) + torch.tensor([10.0, 10.0])
        cluster3 = torch.randn(30, 2) + torch.tensor([-10.0, 10.0])
        self.x = torch.concat([cluster1, cluster2, cluster3], dim=0)
        self.n_clusters = 3

    def test_kmeans_basic_functionality(self) -> None:
        (centers, labels) = pt_kmeans.kmeans(self.x, self.n_clusters)
        self.assertEqual(centers.shape, (self.n_clusters, self.x.shape[1]))
        self.assertEqual(labels.shape, (self.x.shape[0],))

        # Check that all cluster IDs are in valid range
        self.assertTrue(torch.all(labels >= 0))
        self.assertTrue(torch.all(labels < self.n_clusters))

        # Check that we have the right number of unique clusters
        unique_labels = torch.unique(labels)
        self.assertEqual(len(unique_labels), self.n_clusters)

    def test_kmeans_reproducibility(self) -> None:
        (centers1, labels1) = pt_kmeans.kmeans(self.x, self.n_clusters, random_seed=123)
        (centers2, labels2) = pt_kmeans.kmeans(self.x, self.n_clusters, random_seed=123)

        torch.testing.assert_close(centers1, centers2)
        torch.testing.assert_close(labels1, labels2)

    def test_kmeans_different_init_methods(self) -> None:
        (centers_random, labels_random) = pt_kmeans.kmeans(self.x, self.n_clusters, init_method="random")
        (centers_kmeans_pp, labels_kmeans_pp) = pt_kmeans.kmeans(self.x, self.n_clusters, init_method="kmeans++")

        self.assertEqual(centers_random.shape, (self.n_clusters, self.x.shape[1]))
        self.assertEqual(centers_kmeans_pp.shape, (self.n_clusters, self.x.shape[1]))
        self.assertEqual(len(torch.unique(labels_random)), self.n_clusters)
        self.assertEqual(len(torch.unique(labels_kmeans_pp)), self.n_clusters)

    def test_kmeans_different_distance_metrics(self) -> None:
        (centers_l2, labels_l2) = pt_kmeans.kmeans(self.x, self.n_clusters, distance_metric="l2")
        (centers_cosine, labels_cosine) = pt_kmeans.kmeans(self.x, self.n_clusters, distance_metric="cosine")

        self.assertEqual(centers_l2.shape, (self.n_clusters, self.x.shape[1]))
        self.assertEqual(centers_cosine.shape, (self.n_clusters, self.x.shape[1]))
        self.assertEqual(len(torch.unique(labels_l2)), self.n_clusters)
        self.assertEqual(len(torch.unique(labels_cosine)), self.n_clusters)

    def test_kmeans_chunked_processing(self) -> None:
        (centers_full, labels_full) = pt_kmeans.kmeans(self.x, self.n_clusters, chunk_size=None, random_seed=2)
        (centers_chunked, labels_chunked) = pt_kmeans.kmeans(self.x, self.n_clusters, chunk_size=10, random_seed=2)

        # Results should be identical
        torch.testing.assert_close(centers_full, centers_chunked)
        torch.testing.assert_close(labels_full, labels_chunked)

    def test_kmeans_early_convergence(self) -> None:
        (centers, labels) = pt_kmeans.kmeans(self.x, self.n_clusters, max_iters=1000, tol=1.0)

        # Should still return valid results
        self.assertEqual(centers.shape, (self.n_clusters, self.x.shape[1]))
        self.assertEqual(labels.shape, (self.x.shape[0],))

    def test_kmeans_single_cluster(self) -> None:
        (centers, labels) = pt_kmeans.kmeans(self.x, n_clusters=1)

        self.assertEqual(centers.shape, (1, self.x.shape[1]))
        self.assertTrue(torch.all(labels == 0))

        # Center should be approximately the mean of all data
        expected_center = self.x.mean(dim=0)
        torch.testing.assert_close(centers[0], expected_center, atol=1e-1, rtol=1e-1)

    def test_kmeans_with_initial_centers(self) -> None:
        torch.manual_seed(0)
        cluster1_data = torch.randn(20, 2) + torch.tensor([1.0, 1.0])
        cluster2_data = torch.randn(20, 2) + torch.tensor([5.0, 5.0])
        cluster3_data = torch.randn(20, 2) + torch.tensor([10.0, 1.0])
        data = torch.concat([cluster1_data, cluster2_data, cluster3_data], dim=0)
        n_clusters = 3

        initial_centers_val = torch.tensor(
            [
                [1.0, 1.0],
                [5.0, 5.0],
                [10.0, 1.0],
            ],
            dtype=data.dtype,
            device=data.device,
        )

        (centers, labels) = pt_kmeans.kmeans(data, n_clusters, initial_centers=initial_centers_val)
        self.assertEqual(centers.shape, (n_clusters, data.shape[1]))
        self.assertEqual(labels.shape, (data.shape[0],))

        # Check if passing an init_method alongside initial_centers results in the same outcome
        (centers_ignored_init, labels_ignored_init) = pt_kmeans.kmeans(
            data, n_clusters, random_seed=123, initial_centers=initial_centers_val
        )
        (centers_ignored_init_pp, labels_ignored_init_pp) = pt_kmeans.kmeans(
            data, n_clusters, init_method="kmeans++", random_seed=123, initial_centers=initial_centers_val
        )

        torch.testing.assert_close(centers_ignored_init, centers_ignored_init_pp)
        torch.testing.assert_close(labels_ignored_init, labels_ignored_init_pp)


class TestHierarchicalKMeans(unittest.TestCase):
    def setUp(self) -> None:
        torch.manual_seed(0)
        self.x = torch.randn(200, 5)
        self.n_clusters = [50, 10, 3]

    def test_hierarchical_kmeans_basic(self) -> None:
        results = pt_kmeans.hierarchical_kmeans(self.x, self.n_clusters)

        self.assertEqual(len(results), len(self.n_clusters))

        # Check shapes for each level
        for i, result in enumerate(results):
            expected_n_clusters = self.n_clusters[i]
            self.assertEqual(result["centers"].shape, (expected_n_clusters, self.x.shape[1]))
            self.assertEqual(result["assignment"].shape, (self.x.shape[0],))

            self.assertTrue(torch.all(result["assignment"] >= 0))
            self.assertTrue(torch.all(result["assignment"] < expected_n_clusters))

    def test_hierarchical_kmeans_consistency(self) -> None:
        results = pt_kmeans.hierarchical_kmeans(self.x, self.n_clusters, random_seed=123)
        for idx, num_clusters in enumerate(self.n_clusters):
            unique_assignments = torch.unique(results[idx]["assignment"])
            self.assertEqual(len(unique_assignments), num_clusters)

    def test_hierarchical_kmeans_single_level(self) -> None:
        results = pt_kmeans.hierarchical_kmeans(self.x, [5])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["centers"].shape, (5, self.x.shape[1]))
        self.assertEqual(results[0]["assignment"].shape, (self.x.shape[0],))

    def test_hierarchical_kmeans_reproducibility(self) -> None:
        results1 = pt_kmeans.hierarchical_kmeans(self.x, self.n_clusters, random_seed=123)
        results2 = pt_kmeans.hierarchical_kmeans(self.x, self.n_clusters, random_seed=123)

        for r1, r2 in zip(results1, results2):
            torch.testing.assert_close(r1["centers"], r2["centers"])
            torch.testing.assert_close(r1["assignment"], r2["assignment"])


class TestSplitCluster(unittest.TestCase):
    def setUp(self) -> None:
        torch.manual_seed(0)
        # Create data with clear clusters
        self.x = torch.tensor(
            [
                [1.0, 1.0],
                [1.1, 1.1],
                [1.2, 1.2],
                [1.3, 1.3],  # Cluster 0 data
                [5.0, 5.0],
                [5.1, 5.1],
                [5.2, 5.2],
                [5.3, 5.3],  # Cluster 1 data
                [10.0, 10.0],
                [10.1, 10.1],
                [10.2, 10.2],
                [10.3, 10.3],  # Cluster 2 data
            ]
        )
        self.labels = torch.tensor([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2])
        self.n_original_clusters = 3

    def test_split_cluster_shape(self) -> None:
        (new_centers, new_labels) = pt_kmeans.split_cluster(self.x, self.labels, cluster_id=1, n_clusters=2)

        # New centers should have shape (n_clusters, n_features)
        self.assertEqual(new_centers.shape, (2, self.x.shape[1]))

        # New labels should have same shape as original
        self.assertEqual(new_labels.shape, self.labels.shape)

    def test_split_cluster_label_values(self) -> None:
        (_, new_labels) = pt_kmeans.split_cluster(self.x, self.labels, cluster_id=1, n_clusters=2)

        # Original clusters 0 and 2 should remain unchanged
        torch.testing.assert_close(new_labels[self.labels == 0], self.labels[self.labels == 0])
        torch.testing.assert_close(new_labels[self.labels == 2], self.labels[self.labels == 2])

        # Cluster 1 should be split into two new labels
        split_labels = new_labels[self.labels == 1]
        unique_split_labels = torch.unique(split_labels)

        # One of the split labels should be the original cluster_id
        self.assertIn(1, unique_split_labels.tolist())

        # Should have exactly 2 unique cluster labels among the split points
        self.assertEqual(len(unique_split_labels), 2)

    def test_split_cluster_preserves_original_data(self) -> None:
        original_x = self.x.clone()
        original_labels = self.labels.clone()

        pt_kmeans.split_cluster(self.x, self.labels, cluster_id=1, n_clusters=2)

        # Original data and labels should be unchanged
        torch.testing.assert_close(self.x, original_x)
        torch.testing.assert_close(self.labels, original_labels)
