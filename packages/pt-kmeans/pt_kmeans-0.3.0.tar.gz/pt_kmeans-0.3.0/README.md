# PyTorch KMeans

## Introduction

`pt_kmeans` is a pure PyTorch implementation of the popular K-Means clustering algorithm, designed for seamless integration into PyTorch-based machine learning pipelines. It offers high performance on both CPU and GPU (CUDA), along with advanced features like K-Means++ initialization, hierarchical clustering, and cluster splitting, all while maintaining full PyTorch tensor compatibility.

Unlike K-Means implementations that require data transfers to NumPy or other libraries, `pt_kmeans` keeps your data on the PyTorch device (CPU or GPU) throughout the entire process, minimizing overhead and maximizing efficiency for large-scale datasets.

## Features

- **Pure PyTorch**: No external dependencies beyond PyTorch itself. All computations are performed using PyTorch tensors, making it ideal for integration with deep learning workflows.
- **Self-Contained & Portable**: The entire implementation resides in a single file, allowing for easy integration by simply copying the file into your project or an existing module.
- **CPU & GPU Support**: Leverages your available hardware. Optimized for CPU performance and efficient on GPUs.
- **K-Means++ Initialization**: Intelligent seeding of initial centroids for faster convergence and better clustering results.
- **L2 and Cosine Distance**: Supports the standard Euclidean (L2) distance and Cosine distance for various data types and applications (e.g., embeddings).
- **Chunked Distance Computations**: Enhances memory efficiency by enabling chunked processing of distance calculations directly within the `_compute_distance` function. This mechanism is leveraged by both cluster assignment (`_assign_clusters`) and K-Means++ initialization (`_kmeans_plusplus_init`), allowing for handling extremely large datasets and preventing Out-Of-Memory (OOM) errors on memory-constrained devices.
- **Reproducibility**: Full control over randomness via `random_seed` for consistent results.
- **Hierarchical K-Means**: Implements a bottom-up hierarchical clustering approach, useful for creating multi-level cluster structures.
- **Cluster Splitting**: Provides a utility to refine existing clusters by splitting a single cluster into multiple sub-clusters.

## Installation

`pt_kmeans` requires PyTorch (`torch>=2.4.0` recommended).

First, ensure you have PyTorch installed (refer to the [official PyTorch website](https://pytorch.org/get-started/locally/) for installation instructions specific to your system and CUDA version).

Then, install `pt_kmeans` directly from PyPI:

```bash
pip install pt_kmeans
```

## Quick Start & Usage Examples

Here's how to get started with `pt_kmeans`.

```python
import torch
import matplotlib.pyplot as plt  # For visualization

from pt_kmeans import hierarchical_kmeans
from pt_kmeans import kmeans
from pt_kmeans import predict
from pt_kmeans import split_cluster
```

### Basic K-Means Clustering

```python
# 1. Generate some synthetic data for demonstration
# Three distinct clusters
data = torch.cat([
    torch.randn(100, 2) * 0.5 + torch.tensor([0.0, 0.0]),
    torch.randn(100, 2) * 0.5 + torch.tensor([5.0, 5.0]),
    torch.randn(100, 2) * 0.5 + torch.tensor([0.0, 5.0]),
])

# Move data to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
data = data.to(device)

n_clusters = 3
random_seed = 0

# 2. Run K-Means
print(f"Running K-Means on {device}...")
(centers, labels) = kmeans(
    data,
    n_clusters=n_clusters,
    max_iters=100,
    tol=1e-4,
    distance_metric="l2",      # or "cosine"
    init_method="kmeans++",    # or "random"
    chunk_size=None,           # Process all at once
    random_seed=random_seed,
)

print("\nK-Means Results:")
print(f"Final Centers Shape: {centers.shape}")
print(f"First 5 Labels: {labels[:5]}")
print(f"Unique Labels: {torch.unique(labels)}")

# 3. (Optional) Visualize the clusters
plt.figure(figsize=(8, 6))
plt.scatter(data[:, 0].cpu(), data[:, 1].cpu(), c=labels.cpu(), cmap="viridis", s=10, alpha=0.7)
plt.scatter(centers[:, 0].cpu(), centers[:, 1].cpu(), c="red", marker="X", s=200, label="Centers")
plt.title("K-Means Clustering Result")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.legend()
plt.grid(True)
plt.show()
```

### Assigning New Data with `predict`

After training, assign new data points to the learned clusters.

```python
# Use the 'centers' obtained from the basic K-Means example
# Generate some new data
new_data = torch.concat([
    torch.randn(10, 2) * 0.5 + torch.tensor([0.2, 0.2]),
    torch.randn(10, 2) * 0.5 + torch.tensor([5.2, 5.2]),
]).to(device)

print(f"\nAssigning new data points using 'predict' on {device}...")
new_labels = predict(
    new_data,
    centers, # Use the centers from the previous kmeans run
    distance_metric="l2",
)

print(f"New Data Shape: {new_data.shape}")
print(f"Labels for new data: {new_labels.tolist()}")
print(f"Unique labels for new data: {torch.unique(new_labels).tolist()}")

# (Optional) Visualize new data with existing clusters
plt.figure(figsize=(8, 6))
plt.scatter(data[:, 0].cpu(), data[:, 1].cpu(), c=labels.cpu(), cmap="viridis", s=10, alpha=0.3, label="Training Data")
plt.scatter(centers[:, 0].cpu(), centers[:, 1].cpu(), c="red", marker="X", s=200, label="Centers")
plt.scatter(
    new_data[:, 0].cpu(),
    new_data[:, 1].cpu(),
    c=new_labels.cpu(),
    marker="o",
    edgecolors="black",
    s=100,
    linewidth=1.5,
    cmap="viridis",
    label="New Data",
)
plt.title("Prediction on New Data")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.legend()
plt.grid(True)
plt.show()
```

### Hierarchical K-Means

Build a multi-level clustering structure.

```python
# Use the 'data' generated in the previous example
n_clusters_levels = [15, 5, 3] # Define number of clusters for each level

print(f"Running Hierarchical K-Means on {device}...")
results = hierarchical_kmeans(
    data,
    n_clusters=n_clusters_levels,
    max_iters=100,
    tol=1e-4,
    distance_metric="l2",
    init_method="kmeans++",
    random_seed=random_seed,
)

print("\nHierarchical K-Means Results:")
for i, level_result in enumerate(results):
    print(f"Level {i} (n_clusters={n_clusters_levels[i]}):")
    print(f"  Centers Shape: {level_result['centers'].shape}")
    print(f"  Assignment Shape (original data): {level_result['assignment'].shape}")
    print(f"  Unique Assignments: {torch.unique(level_result['assignment'])}")
```

### Splitting an Existing Cluster

Refine a specific cluster by breaking it down into sub-clusters.

```python
# First, run a basic K-Means to get initial labels and centers
(initial_centers, initial_labels) = kmeans(
    data, n_clusters=3, random_seed=random_seed, show_progress=False
)

cluster_to_split_id = 0  # Choose a cluster to split
num_sub_clusters = 2

print(f"Splitting Cluster {cluster_to_split_id} into {num_sub_clusters} sub-clusters on {device}...")
(new_sub_centers, updated_labels) = split_cluster(
    data,
    initial_labels,
    cluster_id=cluster_to_split_id,
    n_clusters=num_sub_clusters,
    max_iters=50,
    distance_metric="l2",
    random_seed=random_seed + 1,
)

print("\nCluster Splitting Results:")
print(f"New Sub-Centers Shape: {new_sub_centers.shape}")
print(f"Updated Labels Shape: {updated_labels.shape}")
print(f"Unique Labels in updated set: {torch.unique(updated_labels).tolist()}")

# Verify that the original cluster_id is replaced by new ones or kept, and new ones are introduced
print(f"Original unique labels: {torch.unique(initial_labels).tolist()}")
print(f"Updated unique labels: {torch.unique(updated_labels).tolist()}")
```

### GPU Usage

To use your GPU, simply ensure your input tensor `x` is on a CUDA device:

```python
x_gpu = torch.randn(1_000_000, 128, device="cuda")  # Create data directly on GPU
n_clusters_gpu = 100

(centers_gpu, labels_gpu) = kmeans(
    x_gpu,
    n_clusters=n_clusters_gpu,
    distance_metric="cosine",  # Often used for embeddings on GPU
    chunk_size=64000,          # Important for larger datasets on GPU to manage memory
    show_progress=True,
)

print(f"GPU K-Means finished. Centers on: {centers_gpu.device}, Labels on: {labels_gpu.device}")
```

## Contributing

Contributions are very welcome! If you find a bug, have a feature request, or want to contribute code, please feel free to:

1. Open an issue on the [GitLab Issues page](https://gitlab.com/hassonofer/pt_kmeans/issues).
2. Submit a Pull Request.

Please ensure your code adheres to the existing style (Black, isort) and passes all tests.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](https://gitlab.com/hassonofer/pt_kmeans/blob/main/LICENSE) file for details.
