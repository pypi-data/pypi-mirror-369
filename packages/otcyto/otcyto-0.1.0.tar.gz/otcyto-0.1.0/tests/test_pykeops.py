from otcyto.check_pykeops import check_pykeops

__author__ = "gunthergl_r2"
__copyright__ = "gunthergl_r2"
__license__ = "MIT"

n = 1e1


def test_otd_loss_pykeops():
    assert check_pykeops(), "geomloss with pykeops is not working"
