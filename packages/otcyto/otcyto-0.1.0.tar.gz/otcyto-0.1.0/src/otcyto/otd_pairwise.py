import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from geomloss import SamplesLoss
from torch.autograd import grad

from otcyto.plot.figure_clouds import figure_clouds

# from otcyto.plot.figure_umap import figure_umap

TensorLike = torch.Tensor
PathLike = str | Path
default_loss = SamplesLoss(loss="sinkhorn", p=2, blur=0.05, scaling=0.8)


class OTDPairwise:
    """
    Compute pairwise Optimal Transport Distances (OTD) between sources and targets.

    Args:
        sources (Sequence[TensorLike]):
            list of data elements which should be "transported" to the targets
        targets (Sequence[TensorLike]):
            list of data elements which the sources should be "transported" to
        sources_names (list[str] | None, optional):
            Optional names for sources. Defaults to ["sample_0", ...].
        targets_names (list[str] | None, optional):
            Optional names for targets. Defaults to ["sample_0", ...].
        loss (SamplesLoss, optional):
            GeomLoss objective to compute OTD. Defaults to
            `SamplesLoss(loss="sinkhorn", p=2, blur=0.05, scaling=0.8)`.
        verbose (bool, optional):
            If True, prints brief progress information.. Defaults to False.
        intermediate_file (PathLike | None, optional):
            If set, writes a CSV of pairwise OTDs after each update.
        skipping_fun (Callable[[int, int], bool], optional):
            Callback returning True to skip computing (i, j).
    """

    def __init__(
        self,
        sources: list[TensorLike],
        targets: list[TensorLike],
        sources_names: list[str] | None = None,
        targets_names: list[str] | None = None,
        loss: SamplesLoss = default_loss,
        verbose: bool = False,
        intermediate_file: PathLike | None = None,
        calculate_brenier: bool = False,
        skipping_fun: Callable[[int, int], bool] = lambda i, j: False,
    ) -> None:
        self.sources = sources
        self.targets = targets
        self.sources_names: list[str] = (
            sources_names if sources_names is not None else [f"sample_{i}" for i in range(len(self.sources))]
        )
        self.targets_names: list[str] = (
            targets_names if targets_names is not None else [f"sample_{i}" for i in range(len(self.targets))]
        )

        if len(self.sources) != len(self.sources_names):
            raise ValueError("len(sources) must equal len(sources_names).")
        if len(self.targets) != len(self.targets_names):
            raise ValueError("len(targets) must equal len(targets_names).")

        self.calculate_brenier: bool = calculate_brenier
        self.loss: SamplesLoss = loss
        self.verbose: bool = verbose
        self._intermediate_file: PathLike | None = intermediate_file
        self._skipping_fun: Callable[[int, int], bool] = skipping_fun

        # Matrices to store timings (seconds) and distances.
        ns, nt = len(self.sources), len(self.targets)
        self._time_sec = torch.zeros((ns, nt), dtype=torch.float32)
        self._otd_vals = torch.zeros((ns, nt), dtype=torch.float32)

        # Brenier map cache; a list-of-lists holding torch.Tensors or None.
        self._brenier_maps: list[list[TensorLike | None]] = [[None for _ in range(nt)] for _ in range(ns)]
        self._otd_calculated: bool = False

        # Validate tensor shapes/dtypes/devices early to avoid cryptic errors later.
        self._validate_inputs()

    # ----------------------------- Internal utilities -----------------------------

    def _validate_inputs(self) -> None:
        """Validate shapes, dtypes, and device compatibility for all tensors."""
        if len(self.sources) == 0 or len(self.targets) == 0:
            raise ValueError("sources and targets must be non-empty.")

    # ----------------------------- Public properties ------------------------------

    @property
    def time_calculation(self) -> pd.DataFrame:
        """Return a (sources x targets) DataFrame of compute times in seconds."""
        return pd.DataFrame(
            self._time_sec.detach().cpu().numpy(),
            index=self.sources_names,
            columns=self.targets_names,
        )

    @property
    def otd_torch(self) -> torch.Tensor:
        """Return a CPU tensor of pairwise OTD values."""
        return self._otd_vals.detach().cpu()

    @property
    def otd_numpy(self) -> np.ndarray:
        """Return a NumPy array of pairwise OTD values."""
        return self.otd_torch.numpy()

    @property
    def otd_df(self) -> pd.DataFrame:
        """Return a (sources x targets) DataFrame of pairwise OTD values."""
        return pd.DataFrame(self.otd_numpy, index=self.sources_names, columns=self.targets_names)

    @property
    def brenier_maps(self) -> list[list[TensorLike | None]]:
        """Access the cached Brenier maps; may be None if not computed."""
        return self._brenier_maps

    # ----------------------------- Persistence -----------------------------------

    def save_intermediate(self, filename: PathLike) -> None:
        """Save the current OTD matrix to CSV."""
        self.otd_df.to_csv(Path(filename))
        if self.verbose:
            print(f"    Wrote {filename}")

    # ----------------------------- Core computation ------------------------------

    def compute(self) -> None:
        """Compute pairwise OTD between every source and target without gradients.

        Notes
        -----
        - This method per default avoids building autograd graphs to stay light.
        - If `self.calculate_brenier` is True, gradients are built only long enough
            to obtain the Brenier map for each computed pair, then discarded.
        - If False, this avoids building autograd graphs; maps can be obtained later
            via `get_brenier_map(i, j)` (which recomputes that pair once).

        """
        ns, nt = len(self.sources), len(self.targets)
        for source_i in range(ns):
            for target_j in range(nt):
                # Skip the pair if skipping_fun returns True
                if self._skipping_fun(source_i, target_j):
                    if self.verbose:
                        print(f"Skipping {self.sources_names[source_i]}" + " -> " + f"{self.targets_names[target_j]}")
                    continue
                if self.verbose:
                    print(
                        "Compute OTD from",
                        self.sources_names[source_i],
                        "to",
                        self.targets_names[target_j],
                        end=" ",
                        flush=True,
                    )
                # Get the source and target samples
                x_i = self.sources[source_i]
                y_j = self.targets[target_j]
                # Time using a monotonic high-resolution timer.
                t0 = time.perf_counter()
                if self.calculate_brenier:
                    loss_val, br_map = self.single_brenier(source=x_i, target=y_j)
                    self._brenier_maps[source_i][target_j] = br_map.detach().cpu()
                    dist_ij = loss_val.detach()
                else:
                    with torch.no_grad():
                        # Compute the optimal transport distance (OTD) using the provided
                        # loss function
                        dist_ij = self.loss(x_i, y_j)
                t1 = time.perf_counter()

                # Store values (detach to be explicit; dist_ij has no grad anyway).
                self._otd_vals[source_i, target_j] = float(dist_ij)
                self._time_sec[source_i, target_j] = float(t1 - t0)

                if self.verbose:
                    print(
                        f"Computed OTD {self.sources_names[source_i]}"
                        + " -> "
                        + "{self.targets_names[target_j]} "
                        + f"= {float(dist_ij):.6g}  (t={t1 - t0:.3f}s)"
                    )

                if self._intermediate_file is not None:
                    # Save the intermediate results to a file if an intermediate
                    #  file path is provided
                    self.save_intermediate(self._intermediate_file)

        self._otd_calculated = True

    def single_brenier(self, source: torch.Tensor, target: torch.Tensor) -> tuple[Any, torch.Tensor]:
        """Calculate the Brenier map for a given source and target.

        Args:
            source (torch.Tensor): The source point cloud.
            target (torch.Tensor): The target point cloud.

        Returns:
            torch.Tensor: The Brenier map as a tensor.
        """

        # https://www.kernel-operations.io/geomloss/_auto_examples/sinkhorn_multiscale/plot_kernel_truncation.html#sphx-glr-auto-examples-sinkhorn-multiscale-plot-kernel-truncation-py
        #  The generalized "Brenier map" is (minus) the gradient of the Sinkhorn loss
        # with respect to the Wasserstein metric:
        self._brenier_maps: list[list[TensorLike | None]]
        # Clone to ensure a leaf tensor with gradients enabled.
        x_leaf = source.detach().clone().requires_grad_(True)
        #  no grad needed for y
        # Compute loss with a live graph.
        loss_val = self.loss(x_leaf, target)
        # Gradient of scalar loss w.r.t. x; retain_graph not needed since we discard it.
        (dx,) = grad(loss_val, (x_leaf,), create_graph=False, retain_graph=False)
        # Map is minus the gradient; scale if needed depending on your convention.
        # Given each point has the same weight, we need to multiply the
        # Brenier map by the number of points in the source
        br_map = (-dx) * x_leaf.shape[0]
        return loss_val, br_map

    def get_brenier_map(self, source_i: int, target_j: int) -> TensorLike:
        """Get the Brenier map for a specific source and target.

        Args:
            source_i (int): Index of the source sample.
            target_j (int): Index of the target sample.

        Returns:
            TensorLike: The Brenier map tensor for the specified pair.
        """
        if not self._otd_calculated:
            raise RuntimeError("OTD must be computed before accessing Brenier maps. Call `.compute()` first.")

        br_map = self._brenier_maps[source_i][target_j]
        if br_map is None:
            # Recompute if not cached
            _, br_map = self.single_brenier(source=self.sources[source_i], target=self.targets[target_j])
        return br_map

    # ----------------------------- Plotting --------------------------------------

    def plot(self, source_i: int = 0, target_j: int = 0, npoints: int = 10_000):
        """Scatter plot of a given source and target sample."""
        fig = figure_clouds(
            self.sources[source_i].detach().cpu(),
            self.targets[target_j].detach().cpu(),
            npoints=npoints,
        )
        return fig

    def plot_brenier(
        self,
        source_i: int = 0,
        target_j: int = 0,
        x_i: int = 0,
        y_i: int = 1,
        color_mapping: str = "#5BBF3AAA",
        npoints: int = 10_000,
    ):
        """Plot source/target clouds and visualize the Brenier map arrows."""
        # Ensure map is computed.
        br_map = self.get_brenier_map(source_i, target_j)

        fig = figure_clouds(
            self.sources[source_i].detach().cpu(),
            self.targets[target_j].detach().cpu(),
            x_i=x_i,
            y_i=y_i,
            map_source_to_target=br_map,
            color_mapping=color_mapping,
            npoints=npoints,
        )
        return fig

    def plot_umap(self, source_i: int = 0, target_j: int = 0):
        raise NotImplementedError("UMAP plotting is not implemented.")
        # fig = figure_umap(
        #     self.sources[source_i].detach().cpu(),
        #     self.targets[target_j].detach().cpu(),
        #     map_source_to_target=self.get_brenier_map(source_i, target_j),
        # )
        # return fig
