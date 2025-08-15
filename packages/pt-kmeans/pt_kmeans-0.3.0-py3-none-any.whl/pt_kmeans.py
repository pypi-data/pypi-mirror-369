import logging
from typing import Literal
from typing import Optional

import torch
import torch.nn.functional as F
from tqdm import tqdm

__version__ = "v0.3.0"

logger = logging.getLogger(__name__)


def _compute_distance(
    x: torch.Tensor,
    centers: torch.Tensor,
    distance_metric: Literal["l2", "cosine"] = "l2",
    x_squared_norm: Optional[torch.Tensor] = None,
    chunk_size: Optional[int] = None,
) -> torch.Tensor:
    n_samples = x.size(0)
    if chunk_size is None or chunk_size >= n_samples:
        if distance_metric == "l2":
            if x_squared_norm is None:
                x_squared_norm = torch.sum(x**2, dim=1)

            centers_squared_norm = torch.sum(centers**2, dim=1)
            distances = x_squared_norm[:, None] - 2 * torch.mm(x, centers.t()) + centers_squared_norm[None, :]
            # distances = torch.cdist(x, centers, p=2).square()
        elif distance_metric == "cosine":
            x_norm = F.normalize(x, p=2, dim=1)
            centers_norm = F.normalize(centers, p=2, dim=1)
            similarities = torch.mm(x_norm, centers_norm.t())
            distances = 1 - similarities
        else:
            raise ValueError(f"Unknown distance_metric: {distance_metric}")

        return distances

    distance_list = []
    n_iters = (n_samples + chunk_size - 1) // chunk_size
    for chunk_idx in range(n_iters):
        begin_idx = chunk_idx * chunk_size
        end_idx = min(n_samples, (chunk_idx + 1) * chunk_size)
        x_chunk = x[begin_idx:end_idx]
        x_squared_norm_chunk = x_squared_norm[begin_idx:end_idx] if x_squared_norm is not None else None
        if distance_metric == "l2":
            if x_squared_norm_chunk is None:
                x_squared_norm_chunk = torch.sum(x_chunk**2, dim=1)

            centers_squared_norm = torch.sum(centers**2, dim=1)
            distances_chunk = (
                x_squared_norm_chunk[:, None] - 2 * torch.mm(x_chunk, centers.t()) + centers_squared_norm[None, :]
            )
        elif distance_metric == "cosine":
            x_norm_chunk = F.normalize(x_chunk, p=2, dim=1)
            centers_norm = F.normalize(centers, p=2, dim=1)
            similarities_chunk = torch.mm(x_norm_chunk, centers_norm.t())
            distances_chunk = 1 - similarities_chunk
        else:
            raise ValueError(f"Unknown distance_metric: {distance_metric}")

        distance_list.append(distances_chunk)

    return torch.concat(distance_list, dim=0)


def _kmeans_plusplus_init(
    x: torch.Tensor,
    n_clusters: int,
    distance_metric: Literal["l2", "cosine"] = "l2",
    show_progress: bool = False,
    generator: Optional[torch.Generator] = None,
    chunk_size: Optional[int] = None,
) -> torch.Tensor:
    """
    Initialize cluster centers using K-Means++ algorithm

    K-Means++ selects initial cluster centers that are far apart from each other,
    leading to better convergence compared to random initialization.

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    n_clusters
        Number of clusters to initialize.
    distance_metric
        Distance metric to use.
    show_progress
        If True, display a progress bar during processing.
    generator
        Random number generator for reproducibility.
    chunk_size
        Number of data points to process in a single batch during distance computations.

    Returns
    -------
    Initial cluster centers of shape (n_clusters, n_features).

    References
    ----------
    .. [1] D. Arthur and S. Vassilvitskii, "k-means++: the advantages of
       careful seeding", Proceedings of the Eighteenth Annual ACM-SIAM Symposium
       on Discrete Algorithms, 2007.

    Examples
    --------
    >>> X = torch.randn(100, 2)  # 100 samples, 2 features
    >>> centers = _kmeans_plusplus_init(X, n_clusters=5)
    >>> centers.shape
    torch.Size([5, 2])
    """

    (n_samples, n_features) = x.shape
    centers = torch.empty((n_clusters, n_features), dtype=x.dtype, device=x.device)
    x_squared_norm = None
    if distance_metric == "l2":
        x_squared_norm = torch.sum(x**2, dim=1)

    # Choose first center randomly
    first_idx = torch.randint(0, n_samples, (1,), device=x.device, generator=generator)
    centers[0] = x[first_idx]

    # Initialize min_distances with distances to the first center
    min_distances = _compute_distance(x, centers[0:1], distance_metric, x_squared_norm).squeeze(1)

    # Choose remaining centers
    for i in tqdm(range(1, n_clusters), desc="K-Means++ initialization", leave=False, disable=not show_progress):
        probabilities = min_distances / (min_distances.sum() + 1e-12)
        cumulative_probs = torch.cumsum(probabilities, dim=0)

        # Sample using inverse transform sampling
        r = torch.rand(1, device=x.device, generator=generator)
        selected_idx = torch.searchsorted(cumulative_probs, r, right=True)
        selected_idx = torch.clamp(selected_idx, 0, n_samples - 1)
        centers[i] = x[selected_idx]

        # Update min_distances only with the newly added center, if more centers are yet to be picked
        if i < n_clusters - 1:
            new_center_distances = _compute_distance(x, centers[i : i + 1], distance_metric, x_squared_norm, chunk_size)
            min_distances = torch.minimum(min_distances, new_center_distances.squeeze(1))

    return centers


def initialize_centers(
    x: torch.Tensor,
    n_clusters: int,
    method: Literal["random", "kmeans++"] = "kmeans++",
    distance_metric: Literal["l2", "cosine"] = "l2",
    show_progress: bool = False,
    generator: Optional[torch.Generator] = None,
    chunk_size: Optional[int] = None,
) -> torch.Tensor:
    """
    Initialize centers for K-Means clustering

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    n_clusters
        Number of clusters to initialize.
    method
        Initialization method.
    distance_metric
        Distance metric to use.
    show_progress
        If True, display a progress bar during processing.
    generator
        Random number generator for reproducibility.
    chunk_size
        Number of data points to process in a single batch during distance computations.

    Returns
    -------
    Initial cluster centers of shape (n_clusters, n_features).
    """

    if method == "random":
        indices = torch.multinomial(
            torch.ones(x.size(0), dtype=torch.float32), n_clusters, replacement=False, generator=generator
        )
        centers = x[indices].to(device=x.device, dtype=x.dtype)
    elif method == "kmeans++":
        centers = _kmeans_plusplus_init(x, n_clusters, distance_metric, show_progress, generator, chunk_size)
    else:
        raise ValueError(f"Unknown initialization method: {method}")

    return centers


def _assign_clusters(
    x: torch.Tensor,
    centers: torch.Tensor,
    distance_metric: Literal["l2", "cosine"] = "l2",
    chunk_size: Optional[int] = None,
) -> torch.Tensor:
    """
    Assign each data point to the nearest cluster center

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    centers
        Cluster centers of shape (n_clusters, n_features).
    distance_metric
        Distance metric to use:
        - "l2": L2 distance
        - "cosine": Cosine distance (1 - cosine similarity)
    chunk_size
        Number of data points to process in a single batch during distance computations.

    Returns
    -------
    Cluster assignments of shape (n_samples,) with values in [0, n_clusters).

    Examples
    --------
    >>> X = torch.randn(100, 2)
    >>> centers = torch.randn(5, 2)
    >>> cluster_ids = assign_clusters(X, centers, distance_metric="l2")
    >>> cluster_ids.shape
    torch.Size([100])
    """

    all_distances = _compute_distance(x, centers, distance_metric, chunk_size=chunk_size)
    cluster_ids = torch.argmin(all_distances, dim=1)
    return cluster_ids


def _update_centers(
    x: torch.Tensor, labels: torch.Tensor, n_clusters: int, generator: Optional[torch.Generator] = None
) -> torch.Tensor:
    """
    Update centers as the mean of assigned points

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    labels
        Cluster assignments of shape (n_samples,).
    n_clusters
        Number of clusters.
    generator
        Random number generator for reproducibility.

    Returns
    -------
    Updated centers of shape (n_clusters, n_features).
    """

    n_features = x.shape[1]
    device = x.device
    new_centers = torch.zeros(n_clusters, n_features, dtype=x.dtype, device=device)

    ids = torch.argsort(labels)
    sorted_cluster_assignment = labels[ids]
    cluster_values = torch.arange(n_clusters, device=labels.device)
    index_split = torch.searchsorted(sorted_cluster_assignment, cluster_values)
    clusters = torch.tensor_split(ids, index_split[1:].cpu())

    for i in range(n_clusters):
        if len(clusters[i]) > 0:
            new_centers[i] = torch.mean(x[clusters[i]], dim=0)
        else:
            # Handle empty clusters by keeping previous center or reinitializing
            # here we'll reinitialize randomly)
            logger.warning(f"Empty cluster {i} detected. Reinitializing randomly.")
            new_centers[i] = x[torch.randint(0, x.shape[0], (1,), device=device, generator=generator)]

    return new_centers


def kmeans(
    x: torch.Tensor,
    n_clusters: int,
    max_iters: int = 100,
    tol: float = 1e-4,
    distance_metric: Literal["l2", "cosine"] = "l2",
    init_method: Literal["random", "kmeans++"] = "kmeans++",
    chunk_size: Optional[int] = None,
    show_progress: bool = False,
    random_seed: Optional[int] = None,
    *,
    initial_centers: Optional[torch.Tensor] = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Perform K-Means clustering

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    n_clusters
        Number of clusters.
    max_iters
        Maximum number of iterations.
    tol
        Tolerance for convergence (normalized change in centers).
    distance_metric
        Distance metric to use.
    init_method
        Centers initialization method.
    chunk_size
        Number of data points to process in a single batch during distance computations.
    show_progress
        If True, display a progress bar during processing.
    random_seed
        Random seed for reproducibility. If None, uses default random state.
    initial_centers
        Optional tensor of initial cluster centers of shape (n_clusters, n_features).
        If provided, the 'init_method' is ignored and clustering starts from these centers.

    Returns
    -------
    A tuple containing:
    - Final centers of shape (n_clusters, n_features)
    - Final cluster assignments of shape (n_samples,)
    """

    # Input validation
    if n_clusters <= 0:
        raise ValueError("n_clusters must be positive")
    if n_clusters > x.size(0):
        raise ValueError("n_clusters cannot exceed number of samples")
    if x.size(0) == 0:
        raise ValueError("Input data cannot be empty")
    if x.dim() != 2:
        raise ValueError("Input data must be 2-dimensional")
    if torch.isnan(x).any():
        raise ValueError("Input data contains NaN values")
    if torch.isinf(x).any():
        raise ValueError("Input data contains infinite values")

    generator = None
    if random_seed is not None:
        generator = torch.Generator(device=x.device)
        generator.manual_seed(random_seed)

    if initial_centers is not None:
        if initial_centers.shape != (n_clusters, x.shape[1]):
            raise ValueError(
                f"initial_centers must have shape ({n_clusters}, {x.shape[1]}), " f"but got {initial_centers.shape}"
            )

        # Ensure initial_centers are on the correct device and dtype
        centers = initial_centers.to(device=x.device, dtype=x.dtype)
    else:
        centers = initialize_centers(x, n_clusters, init_method, distance_metric, show_progress, generator, chunk_size)

    prev_centers = centers.clone()
    for _ in tqdm(range(max_iters), desc="K-Means iterations", leave=False, disable=not show_progress):
        labels = _assign_clusters(x, centers, distance_metric, chunk_size)
        centers = _update_centers(x, labels, n_clusters, generator)

        # Check for convergence
        center_shift = torch.norm(centers - prev_centers) / torch.norm(prev_centers)
        if center_shift < tol:
            break

        prev_centers = centers.clone()

    return (centers, labels)


def hierarchical_kmeans(
    x: torch.Tensor,
    n_clusters: list[int],
    max_iters: int = 100,
    tol: float = 1e-4,
    distance_metric: Literal["l2", "cosine"] = "l2",
    init_method: Literal["random", "kmeans++"] = "kmeans++",
    chunk_size: Optional[int] = None,
    show_progress: bool = False,
    random_seed: Optional[int] = None,
) -> list[dict[str, torch.Tensor]]:
    """
    Run a bottom up hierarchical K-Means

    The hierarchical K-Means algorithm works by:
    1. Level 0: Apply K-Means to the original data
    2. Level 1: Apply K-Means to the centers from Level 0
    3. Level 2: Apply K-Means to the centers from Level 1
    4. Continue until n_levels is reached

    Parameters
    ----------
    x
        Data embeddings of shape (n_samples, n_features).
    n_clusters
        Number of clusters for each level of hierarchical K-Means.
    max_iters
        Maximum number of iterations.
    tol
        Tolerance for convergence (normalized change in centers).
    distance_metric
        Distance metric to use.
    init_method
        Centers initialization method.
    chunk_size
        Number of data points to process in a single batch during distance computations.
    show_progress
        If True, display a progress bar during processing.
    random_seed
        Random seed for reproducibility. If None, uses default random state.

    Returns
    -------
    A list of dictionaries where each dictionary contains:
    - centers: Centers of clusters of shape (n_clusters_level, n_features)
    - assignment: Mapping from original data to cluster indices of shape (n_samples,)

    Examples
    --------
    >>> data = torch.randn(1000, 50)  # 1000 samples, 50 features
    >>> results = hierarchical_kmeans(data, n_clusters=[100, 20, 5])
    >>> results[0]["centers"].shape  # Level 0: 100 clusters from 1000 points
    torch.Size([100, 50])
    >>> results[1]["centers"].shape  # Level 1: 20 clusters from 100 centers
    torch.Size([20, 50])
    >>> results[2]["centers"].shape  # Level 2: 5 clusters from 20 centers
    torch.Size([5, 50])
    """

    # Input validation
    if x.size(0) == 0:
        raise ValueError("Input data cannot be empty")
    if any(nc <= 0 for nc in n_clusters):
        raise ValueError("All values in n_clusters must be positive")

    n_levels = len(n_clusters)
    results: list[dict[str, torch.Tensor]] = []
    current_level_assignments = torch.empty(0)
    for level in range(n_levels):
        if level == 0:
            data = x  # First level: use original data
        else:
            data = results[level - 1]["centers"]  # Subsequent levels: use previous centers

        (centers, center_assignment) = kmeans(
            data,
            n_clusters=n_clusters[level],
            max_iters=max_iters,
            tol=tol,
            distance_metric=distance_metric,
            init_method=init_method,
            chunk_size=chunk_size,
            show_progress=show_progress,
            random_seed=random_seed,
        )

        if level == 0:
            original_assignment = center_assignment
        else:
            original_assignment = center_assignment[current_level_assignments]

        results.append(
            {
                "centers": centers,
                "assignment": original_assignment,
            }
        )

        current_level_assignments = original_assignment

    return results


def split_cluster(
    x: torch.Tensor,
    labels: torch.Tensor,
    cluster_id: int,
    n_clusters: int,
    max_iters: int = 100,
    tol: float = 1e-4,
    distance_metric: Literal["l2", "cosine"] = "l2",
    init_method: Literal["random", "kmeans++"] = "kmeans++",
    chunk_size: Optional[int] = None,
    show_progress: bool = False,
    random_seed: Optional[int] = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Split an existing cluster into multiple sub-clusters using K-Means

    This function extracts all data points belonging to a specific cluster
    and applies K-Means clustering to split them into n_clusters sub-clusters.

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    labels
        Current cluster assignments of shape (n_samples,).
    cluster_id
        ID of the cluster to split.
    n_clusters
        Number of sub-clusters to create from the split.
    max_iters
        Maximum number of iterations.
    tol
        Tolerance for convergence (normalized change in centers).
    distance_metric
        Distance metric to use.
    init_method
        Centers initialization method.
    chunk_size
        Number of data points to process in a single batch during distance computations.
    show_progress
        If True, display a progress bar during processing.
    random_seed
        Random seed for reproducibility. If None, uses default random state.

    Returns
    -------
    A tuple containing:
    - New centers of the sub-clusters of shape (n_clusters, n_features)
    - Updated labels of shape (n_samples,) where the original cluster_id is replaced with new cluster IDs.
    """

    # Input validation
    if cluster_id not in labels:
        raise ValueError(f"Cluster ID {cluster_id} not found in labels")
    if n_clusters <= 1:
        raise ValueError("n_clusters must be greater than 1 for splitting")

    cluster_mask = labels == cluster_id
    cluster_data = x[cluster_mask]

    (sub_centers, sub_labels) = kmeans(
        cluster_data,
        n_clusters=n_clusters,
        max_iters=max_iters,
        tol=tol,
        distance_metric=distance_metric,
        init_method=init_method,
        chunk_size=chunk_size,
        show_progress=show_progress,
        random_seed=random_seed,
    )

    max_label = labels.max().item()
    new_labels = labels.clone()
    for sub_label_idx in range(n_clusters):
        sub_cluster_indices = torch.where(cluster_mask)[0][sub_labels == sub_label_idx]
        if sub_label_idx == 0:
            new_cluster_id = cluster_id
        else:
            new_cluster_id = max_label + sub_label_idx

        new_labels[sub_cluster_indices] = new_cluster_id

    return (sub_centers, new_labels)


def predict(
    x: torch.Tensor,
    centers: torch.Tensor,
    distance_metric: Literal["l2", "cosine"] = "l2",
    chunk_size: Optional[int] = None,
) -> torch.Tensor:
    """
    Assigns new data points to the closest cluster centers.

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    centers
        Cluster centers of shape (n_clusters, n_features) to which data will be assigned.
    distance_metric
        Distance metric to use:
        - "l2": L2 distance
        - "cosine": Cosine distance (1 - cosine similarity)
    chunk_size
        Number of data points to process in a single batch during distance computations.

    Returns
    -------
    Cluster assignments for 'x' of shape (n_samples,) with values in [0, n_clusters).

    Examples
    --------
    >>> X_train = torch.randn(100, 2)
    >>> centers, _ = pt_kmeans.kmeans(X_train, n_clusters=5)
    >>> X_new = torch.randn(20, 2)
    >>> new_cluster_ids = pt_kmeans.predict(X_new, centers, distance_metric="l2")
    >>> new_cluster_ids.shape
    torch.Size([20])
    """

    return _assign_clusters(x, centers, distance_metric, chunk_size)
