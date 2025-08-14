################################################################################
# Synthetic sphere - a typical source measure:

import numpy as np
import torch


def create_sphere(n_samples: int | float = 1000, use_cuda: bool = True):
    """Creates a uniform sample on the unit sphere.

    Args:
        n_samples (int, optional): Number of samples to generate. Defaults to 1000.
        use_cuda (bool, optional): If True, use CUDA for tensor operations. Defaults to True.

    Returns:
        Tuple[torch.Tensor, torch.Tensor]: A tuple containing:
            - points (torch.Tensor): Tensor of shape (n_samples, 3) with the coordinates of the points on the sphere.
            - weights (torch.Tensor): Tensor of shape (n_samples,) with the weights of the points.
    """
    n_samples = int(n_samples)

    # Indices for generating points
    indices = np.arange(0, n_samples, dtype=float) + 0.5
    # Spherical coordinates
    phi = np.arccos(1 - 2 * indices / n_samples)
    theta = np.pi * (1 + 5**0.5) * indices

    # Cartesian coordinates
    x, y, z = np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)
    points = np.vstack((x, y, z)).T
    # Uniform weights
    weights = np.ones(n_samples) / n_samples

    # Convert to torch tensors
    weights = torch.tensor(weights)
    points = torch.tensor(points)

    # Move to GPU if available and requested
    if torch.cuda.is_available() and use_cuda:
        weights = weights.cuda()
        points = points.cuda()
    return points, weights
