from typing import Any

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.quiver import Quiver
from torch import Tensor

ArrayLike = np.ndarray | Tensor


def _to_numpy(x: ArrayLike, name: str) -> np.ndarray:
    """Convert a torch.Tensor or numpy array to a NumPy float array on CPU."""
    if isinstance(x, Tensor):
        x = x.detach().cpu().numpy()
    if not isinstance(x, np.ndarray):  # type: ignore[unnecessary-isinstance]
        raise TypeError(f"{name} must be a NumPy array or torch.Tensor.")
    if x.ndim != 2:
        raise ValueError(f"{name} must be 2D with shape (n, d); got shape {x.shape}.")
    if x.shape[0] == 0:
        raise ValueError(f"{name} must have at least one row.")
    # Ensure float dtype for matplotlib and quiver scaling
    if not np.issubdtype(x.dtype, np.floating):
        x = x.astype(np.float32, copy=False)
    return np.ascontiguousarray(x)


def display_cloud_mapping(
    ax: Axes,
    x: ArrayLike,
    color: str | np.ndarray,
    x_i: int = 0,
    y_i: int = 1,
    v: ArrayLike | None = None,
    color_mapping: str = "#5BBF3AAA",
    npoints: int | None = None,
    **scatter_kwargs: Any,
) -> tuple[PathCollection, Quiver | None]:
    """
    Scatter a 2D projection of a point cloud and optionally plot a vector field.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes to draw on.
    x : (n, d) array-like of float
        Point cloud; only columns `x_i` and `y_i` are used for plotting.
        Accepts NumPy arrays or torch.Tensors (auto-converted to CPU NumPy).
    color : str or (n,) array-like
        Matplotlib-compatible color specification for the scatter points.
    x_i : int, default=0
        Column index to use as X.
    y_i : int, default=1
        Column index to use as Y.
    v : (n, d) array-like of float, optional
        Vector field aligned with `x` (e.g., a Brenier map). If provided, a
        quiver plot is drawn using components `[x_i, y_i]`.
    color_mapping : str, default="#5BBF3AAA"
        Color for the quiver arrows (supports RGBA hex).
    npoints : int, optional
        If provided, only the first `npoints` rows are plotted (both `x` and `v`).
    *scatter_args, **scatter_kwargs
        Extra arguments forwarded to `Axes.scatter`.

    Returns
    -------
    (PathCollection, Quiver | None)
        The scatter artist and the quiver artist (or None if `v` is None).

    Raises
    ------
    TypeError
        If inputs are not arrays/tensors.
    ValueError
        If shapes are invalid, indices are out of bounds, or lengths mismatch.

    Notes
    -----
    - This function does not random-subsample; it takes the *first* `npoints`.
      For representative subsets on unordered data, consider a random or stratified
      sampler upstream.
    """
    # ---- Normalize & validate inputs ------------------------------------------------
    x_np = _to_numpy(x, "x")

    if not (0 <= x_i < x_np.shape[1]) or not (0 <= y_i < x_np.shape[1]):
        raise ValueError(f"x_i and y_i must be within [0, {x_np.shape[1] - 1}]; got x_i={x_i}, y_i={y_i}.")

    v_np: np.ndarray | None = None
    if v is not None:
        v_np = _to_numpy(v, "v")
        if v_np.shape != x_np.shape:
            raise ValueError(f"v must have the same shape as x; got x{tuple(x_np.shape)} vs v{tuple(v_np.shape)}.")

    # ---- Optional downsampling (deterministic: first n rows) -----------------------
    if npoints is not None:
        if npoints <= 0:
            raise ValueError("npoints must be a positive integer.")
        n = min(npoints, x_np.shape[0])
        x_np = x_np[:n, :]
        if v_np is not None:
            v_np = v_np[:n, :]

    # ---- Scatter plot ---------------------------------------------------------------
    # Use edgecolors="none" to avoid a slow stroke around many tiny points.
    scatter_artist = ax.scatter(
        x_np[:, x_i],
        x_np[:, y_i],
        c=color,
        edgecolors="none",
        **scatter_kwargs,
    )

    # ---- Optional quiver for vector field ------------------------------------------
    quiver_artist: Quiver | None = None
    if v_np is not None:
        quiver_artist = ax.quiver(
            x_np[:, x_i],
            x_np[:, y_i],
            v_np[:, x_i],
            v_np[:, y_i],
            scale=1.0,  # use data units for arrow length
            scale_units="xy",
            color=color_mapping,
            zorder=3,
            width=2e-3,  # thin arrows; adjust as needed for DPI/axes size
        )

    return scatter_artist, quiver_artist
