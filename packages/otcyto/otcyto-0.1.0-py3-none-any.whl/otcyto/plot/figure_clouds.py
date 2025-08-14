from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import torch
from matplotlib.figure import Figure

from otcyto.plot.display_cloud import display_cloud
from otcyto.plot.display_cloud_mapping import display_cloud_mapping


def figure_clouds(
    source_pointcloud: Any,
    target_pointcloud: Any,
    x_i: int = 0,
    y_i: int = 1,
    map_source_to_target: torch.Tensor | None = None,
    color_mapping: str = "#5BBF3AAA",
    label_source: str = "Source",
    label_target: str = "Target",
    color_source: str = "#0000FFA0",
    color_target: str = "#FF0000A0",
    npoints: int | None = 1000,
    *,
    figsize: tuple[float, float] = (12.0, 12.0),
    legend_loc: str = "upper left",
    tight_layout: bool = True,
) -> Figure:
    """Create a figure displaying two 2D point clouds and (optionally) their mapping.

    Parameters
    ----------
    source_pointcloud
        Source points with shape (N, D). Accepts torch.Tensor or any array-like
        that your plotting helpers can consume.
    target_pointcloud
        Target points with shape (M, D). Same accepted types as ``source_pointcloud``.
    x_i, y_i
        Column indices to plot on the x and y axes.
    map_source_to_target
        Optional mapping information passed through to ``display_cloud_mapping``.
        Typically a torch.Tensor describing correspondences or flow-related weights.
    color_mapping
        Color used by the mapping overlay (RGBA hex supported).
    label_source, label_target
        Legend labels for source and target clouds.
    color_source, color_target
        Colors for the source and target scatter points (RGBA hex supported).
    npoints
        If provided, plot at most this many points from each cloud (head of the array).
        Use ``None`` to plot all points.
    figsize
        Matplotlib figure size.
    legend_loc
        Legend location passed to ``plt.legend``.
    tight_layout
        Whether to call ``plt.tight_layout()`` before returning.

    Returns
    -------
    matplotlib.figure.Figure
        The created figure.

    Raises
    ------
    ValueError
        If indices are invalid or ``npoints`` is non-positive (when provided).
    """
    # --- Basic parameter validation (display_* helpers do shape conversion/validation).
    if npoints is not None:
        if not isinstance(npoints, int) or npoints <= 0:  # type: ignore[unnecessary-isinstance]
            raise ValueError("npoints must be a positive integer or None.")

    if not isinstance(x_i, int) or not isinstance(y_i, int):  # type: ignore[unnecessary-isinstance]
        raise ValueError("x_i and y_i must be integers.")
    if x_i == y_i:
        # Usually unintended; helps catch accidental duplicate indices.
        raise ValueError("x_i and y_i must be different columns.")

    # If a mapping is provided and torch is present, lightly validate type.
    if map_source_to_target is not None:
        if not isinstance(map_source_to_target, torch.Tensor):  # type: ignore[unnecessary-isinstance]
            # Keep this soft to avoid importing NumPy here; downstream will error clearly if incompatible.
            raise ValueError("map_source_to_target must be a torch.Tensor if provided.")

    # --- Build figure and single axis.
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1, 1, 1)

    # --- Draw source with mapping overlay (if provided).
    display_cloud_mapping(
        ax=ax,
        x=source_pointcloud,
        color=color_source,
        x_i=x_i,
        y_i=y_i,
        v=map_source_to_target,
        color_mapping=color_mapping,
        label=label_source,
        npoints=npoints,
    )

    # --- Draw target.
    display_cloud(
        ax=ax,
        measure=target_pointcloud,
        color=color_target,
        x_i=x_i,
        y_i=y_i,
        label=label_target,
        npoints=npoints,
    )

    plt.legend(loc=legend_loc)
    if tight_layout:
        plt.tight_layout()

    return fig
