from typing import Any

import numpy as np
from matplotlib.axes import Axes
from numpy.typing import ArrayLike

try:  # Torch is optional at runtime
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore[assignment]
    Tensor = Any  # type: ignore[misc,assignment]


def display_cloud(
    ax: Axes,
    measure: ArrayLike | torch.Tensor,
    color: str | None = None,
    x_i: int = 0,
    y_i: int = 1,
    npoints: int | None = None,
    **kwargs,
):
    """Plot a 2D point cloud on a Matplotlib axis.

    Parameters
    ----------
    ax
        Target Matplotlib axis.
    measure
        Point data with shape (N, D). Accepts NumPy arrays, PyTorch tensors, or any
        array-like convertible to a 2D NumPy array.
    color
        Optional Matplotlib color for points. If omitted, Matplotlib defaults apply.
    x_i
        Column index for x-coordinates (default: 0).
    y_i
        Column index for y-coordinates (default: 1).
    npoints
        If provided, plot at most this many points (from the start).
    **kwargs
        Extra keyword args forwarded to ``ax.scatter`` (e.g., s=4, alpha=0.6).

    Returns
    -------
    PathCollection
        The scatter plot artist returned by ``ax.scatter``.

    """
    # --- Convert input to a NumPy array (copy avoided when possible).
    if torch is not None and isinstance(measure, torch.Tensor):
        # Move to CPU if necessary and detach from graph; convert to NumPy
        np_measure = measure.detach().cpu().numpy()
    else:
        # np.asarray handles list-like inputs; dtype=None preserves numeric dtype
        try:
            np_measure = np.asarray(measure)
        except Exception as exc:  # defensive: non-array-like inputs
            raise TypeError("measure must be array-like or a torch.Tensor") from exc

    # --- Validate dimensionality: need a 2D array with at least 2 columns.
    if np_measure.ndim != 2:
        raise ValueError(f"measure must be 2D, got shape {np_measure.shape!r}")
    n_rows, n_cols = np_measure.shape
    if n_cols < 2:
        raise ValueError(f"measure must have at least 2 columns, got {n_cols}")

    # --- Validate indices.
    if not (0 <= x_i < n_cols) or not (0 <= y_i < n_cols):
        raise ValueError(f"x_i and y_i must be in [0, {n_cols - 1}]; got x_i={x_i}, y_i={y_i}")
    if x_i == y_i:
        # Usually unintended for a 2D scatter; keep explicit to avoid flat lines.
        raise ValueError("x_i and y_i must refer to different columns")

    # --- Optionally downsample to the first npoints rows.
    if npoints is not None:
        if npoints <= 0:
            raise ValueError("npoints must be a positive integer")
        npoints = min(int(npoints), n_rows)
        np_measure = np_measure[:npoints, :]

    # --- Plot with equal aspect for spatial data.
    ax.set_aspect("equal")

    # Respect user-specified color precedence: explicit 'c' in kwargs wins.
    if color is not None and "c" not in kwargs:
        kwargs["c"] = color

    # --- Create scatter plot.
    return ax.scatter(np_measure[:, x_i], np_measure[:, y_i], **kwargs)
