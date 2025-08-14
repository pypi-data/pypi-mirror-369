import pykeops

from otcyto.geomloss.create_sphere import create_sphere
from otcyto.otd_pairwise import OTDPairwise


def check_pykeops():
    from geomloss import SamplesLoss

    source = create_sphere(2)[0]  # 0 element is the pointcloud
    target = create_sphere(2)[0] + 1  # 0 element is the pointcloud

    # tensorized must always work
    otdPW = OTDPairwise(
        [source],
        [target],
        loss=SamplesLoss(loss="sinkhorn", p=2, blur=1e-7, scaling=0.99, backend="tensorized"),
    )
    otdPW.compute()
    assert otdPW._otd_calculated, "Tensorized version MUST work, why doesn't it?"  # pyright: ignore[reportPrivateUsage]

    otdPW = OTDPairwise(
        [source],
        [target],
        loss=SamplesLoss(loss="sinkhorn", p=2, blur=1e-7, scaling=0.99, backend="online"),
    )
    otdPW.compute()
    assert otdPW._otd_calculated, "'online' doesnt work, did you properly install pykeops?"  # pyright: ignore[reportPrivateUsage]

    otdPW = OTDPairwise(
        [source],
        [target],
        loss=SamplesLoss(loss="sinkhorn", p=2, blur=1e-7, scaling=0.99, backend="multiscale"),
    )
    otdPW.compute()
    assert otdPW._otd_calculated, "'multiscale' doesnt work, did you properly install pykeops?"  # pyright: ignore[reportPrivateUsage]

    # https://www.kernel-operations.io/keops/python/installation.html#testing-your-installation
    pykeops.test_numpy_bindings()
    pykeops.test_torch_bindings()
    return True
