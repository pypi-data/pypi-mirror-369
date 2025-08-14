import pytest

from otcyto.geomloss.create_sphere import create_sphere
from otcyto.otd_pairwise import OTDPairwise

__author__ = "gunthergl_r2"
__copyright__ = "gunthergl_r2"
__license__ = "MIT"

n = 1e1


def test_wrong_spheres():
    source = create_sphere(n)[0]  # 0 element is the pointcloud
    target = create_sphere(n)[0] + 1  # 0 element is the pointcloud

    otdPW = OTDPairwise(source, target)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match=r"Input samples 'x' and 'y' should be encoded as"):
        otdPW.compute()


def test_otd_spheres():
    source = create_sphere(n)[0]  # 0 element is the pointcloud
    target = create_sphere(n)[0] + 1  # 0 element is the pointcloud

    otdPW = OTDPairwise([source], [target])
    otdPW.compute()

    assert otdPW.otd_torch.shape == (
        1,
        1,
    ), "OTD result should be a matrix of number of sources x number of targets"


def test_otd_ensure_noBrenier():
    source = create_sphere(n)[0]  # 0 element is the pointcloud
    target = create_sphere(n)[0] + 1  # 0 element is the pointcloud

    otdPW = OTDPairwise([source], [target])
    otdPW.compute()
    assert [[None]] == otdPW._brenier_maps  # pyright: ignore[reportPrivateUsage]


def test_otd_spheres_named():
    source = create_sphere(n)[0]  # 0 element is the pointcloud
    target = create_sphere(n)[0]  # 0 element is the pointcloud
    otdPW = OTDPairwise([source], [target], sources_names=["source"], targets_names=["target"])
    otdPW.compute()


def test_otd_sphere_multiple():
    sources = [create_sphere(npoints)[0] for npoints in [n, n]]
    targets = [create_sphere(npoints)[0] for npoints in [n, n, n, n]]
    otdPW = OTDPairwise(sources, targets)
    assert otdPW.otd_torch.shape == (
        2,
        4,
    ), "OTD result should be a matrix of number of sources x number of targets"

    assert otdPW.otd_torch.shape == (2, 4)
    assert otdPW.otd_df.shape == (2, 4)
    assert otdPW.otd_numpy.shape == (2, 4)


def test_gpu():
    from numpy import ndarray
    from pandas import DataFrame
    from torch import Tensor
    from torch.cuda import is_available

    sources = [create_sphere(npoints)[0] for npoints in [n, n]]
    targets = [create_sphere(npoints)[0] for npoints in [n, n, n, n]]
    if is_available():
        assert sources[0].is_cuda
        assert targets[0].is_cuda
    otdPW = OTDPairwise(sources, targets)
    otdPW.compute()
    assert isinstance(otdPW.otd_df, DataFrame)
    assert isinstance(otdPW.otd_numpy, ndarray)
    assert isinstance(otdPW.otd_torch, Tensor)
    assert otdPW.otd_torch.shape == (
        2,
        4,
    ), "OTD result should be a matrix of number of sources x number of targets"


def test_otd_values():
    import numpy as np

    source = create_sphere(n)[0]  # 0 element is the pointcloud
    target = create_sphere(n)[0]  # 0 element is the pointcloud
    otdPW_source_target = OTDPairwise(
        [source],
        [target + 1, target + 2, target + 3, target - 1, target - 2, target - 3],
    )
    otdPW_target_source = OTDPairwise(
        [target + 1, target + 2, target + 3, target - 1, target - 2, target - 3],
        [source],
    )
    otdPW_same = OTDPairwise([source], [source])

    otdPW_source_target.compute()
    otdPW_target_source.compute()
    otdPW_same.compute()

    assert otdPW_same.otd_numpy[0, 0] == 0, "OTD of the same pointcloud should be 0"

    assert np.allclose(otdPW_source_target.otd_numpy.transpose(), otdPW_target_source.otd_numpy)
    ostv = otdPW_source_target.otd_df.values[0]
    assert ostv[0] == ostv[3], "+-1 should be the same"
    assert ostv[1] == ostv[4], "+-2 should be the same"
    assert ostv[2] == ostv[5], "+-3 should be the same"
    assert otdPW_source_target.otd_df.shape == (
        1,
        6,
    ), "OTD result should be a matrix of number of sources x number of targets"


def test_otd_loss():
    import numpy as np
    from geomloss import SamplesLoss
    from torch import manual_seed, rand

    source = create_sphere(n)[0]  # 0 element is the pointcloud

    manual_seed(3481)
    random_noise = rand(source.shape)

    otdPW = OTDPairwise(
        [source],
        [source + random_noise.to(source.device)],
        loss=SamplesLoss(
            # "sinkhorn":
            # (Un-biased) Sinkhorn divergence, which interpolates between
            #  Wasserstein (blur=0) and kernel (blur=+Inf) distances.
            loss="sinkhorn",
            p=2,
            # The finest level of detail that should be handled by the loss function
            # in order to prevent overfitting on the samples’ locations.
            blur=1e-7,
            # if loss is "sinkhorn", specifies the ratio between successive values of sigma
            # in the epsilon-scaling descent. This parameter allows you to specify the
            # trade-off between speed (scaling < .4) and accuracy (scaling > .9).
            scaling=0.99,
        ),
    )
    otdPW.compute()

    assert np.allclose(
        otdPW.otd_numpy[0, 0],
        0.5556862354278564,
    )


def test_otd_breniermap_compute_missing():
    source = create_sphere(10)[0]  # 0 element is the pointcloud
    target = create_sphere(10)[0] + 1  # 0 element is the pointcloud
    otdPW_1 = OTDPairwise([source], [target])

    print(otdPW_1.brenier_maps)


def test_otd_breniermap():
    source = create_sphere(10)[0]  # 0 element is the pointcloud
    source_1 = create_sphere(10)[0] + 1  # 0 element is the pointcloud
    source_2 = create_sphere(10)[0] + 2  # 0 element is the pointcloud
    otdPW_1 = OTDPairwise([source], [source_1], calculate_brenier=True)
    otdPW_2 = OTDPairwise([source], [source_1, source_2], calculate_brenier=True)
    otdPW_3 = OTDPairwise([source_1, source_2], [source], calculate_brenier=True)

    otdPW_1.compute()
    otdPW_2.compute()
    otdPW_3.compute()

    from torch import allclose, float64, tensor

    # The following assertions check if the computed Brenier maps match the expected values.

    # Check if the Brenier map for the first pair of samples in otdPW_1 is approximately 1
    assert allclose(otdPW_1.brenier_maps[0][0], tensor(1, dtype=float64)), (
        f"Brenier map for otdPW_1 is not as expected: {otdPW_1.brenier_maps[0][0]} != 1"
    )

    # Check if the Brenier map for the first pair of samples in otdPW_2 is approximately 1
    assert allclose(otdPW_2.brenier_maps[0][0], tensor(1, dtype=float64)), (
        f"Brenier map for otdPW_2[0][0] is not as expected: {otdPW_2.brenier_maps[0][0]} != 1"
    )

    # Check if the Brenier map for the second pair of samples in otdPW_2 is approximately 2
    assert allclose(otdPW_2.brenier_maps[0][1], tensor(2, dtype=float64)), (
        f"Brenier map for otdPW_2[0][1] is not as expected: {otdPW_2.brenier_maps[0][1]} != 2"
    )
    # otdPW_3 swapped sources and targets of otdPW_2, thus I expect that the brenier maps
    # are identical except for the sign of the values.
    # Check if the Brenier map for the first pair of samples in otdPW_3 is approximately -1
    assert allclose(otdPW_3.brenier_maps[0][0], tensor(-1, dtype=float64)), (
        f"Brenier map for otdPW_3[0][0] is not as expected: {otdPW_3.brenier_maps[0][0]} != -1"
    )

    # Check if the Brenier map for the first pair of samples in otdPW_3 is approximately -2
    assert allclose(otdPW_3.brenier_maps[1][0], tensor(-2, dtype=float64)), (
        f"Brenier map for otdPW_3[1][0] is not as expected: {otdPW_3.brenier_maps[1][0]} != -2"
    )


def test_otd_save_intermediate():
    source = create_sphere(n)[0]  # 0 element is the pointcloud
    target = create_sphere(n)[0] + 1  # 0 element is the pointcloud

    otdPW = OTDPairwise([source], [target], intermediate_file="removeme.csv")
    otdPW.compute()
    otdPW = OTDPairwise([source, source], [target, target, target], intermediate_file="removeme.csv")
    otdPW.compute()


def test_otd_wrong_samplenames():
    source = create_sphere(n)[0]  # 0 element is the pointcloud
    target = create_sphere(n)[0] + 1  # 0 element is the pointcloud
    with pytest.raises(ValueError, match="len.sources. must equal len.sources_names"):
        otdPW = OTDPairwise(
            [source, source],
            [target, target, target],
            sources_names=["a"],
            targets_names=["a", "b", "c"],
        )
        print(otdPW)


def test_otd_shifted():
    source = create_sphere(n)[0]  # 0 element is the pointcloud
    target = create_sphere(n)[0] + 1  # 0 element is the pointcloud
    source_2 = create_sphere(n)[0] * 2  # 0 element is the pointcloud
    target_2 = (create_sphere(n)[0] + 1) * 2  # 0 element is the pointcloud
    print("test")

    otdPW = OTDPairwise([source, source_2], [target, target_2])
    otdPW.compute()
    otd_usual = otdPW.otd_df
    print(otd_usual)

    # ratio features within the same source should be the same
    import torch

    def custom_ratiofun(x: torch.tensor):
        return torch.vstack(
            (
                x[:, 0] / x[:, 1],
                x[:, 0] / x[:, 2],
                x[:, 1] / x[:, 2],
            ),
        )

    ratio_sources = [custom_ratiofun(x.detach().clone()) for x in [source, source_2]]
    ratio_targets = [custom_ratiofun(x.detach().clone()) for x in [target, target_2]]
    ratio_sources[0]
    ratio_sources[1]
    ratio_targets[0]
    ratio_targets[1]
    otdPW = OTDPairwise(
        [custom_ratiofun(x.detach().clone()) for x in [source, source_2]],
        [custom_ratiofun(x.detach().clone()) for x in [target, target_2]],
    )
    otdPW.compute()
    otd_ratios = otdPW.otd_df

    assert all(otd_ratios == otd_ratios.iloc[1, 1]), "OTD on ratios should be invariant to multiplicative shifts"
