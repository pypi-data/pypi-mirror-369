from otcyto.geomloss.create_sphere import create_sphere
from otcyto.otd_pairwise import OTDPairwise
from otcyto.plot.figure_clouds import figure_clouds

__author__ = "gunthergl_r2"
__copyright__ = "gunthergl_r2"
__license__ = "MIT"

n = 1e3


def test_plots():
    sources = [create_sphere(npoints)[0] for npoints in [n, n]]
    targets = [create_sphere(npoints)[0] + 1 for npoints in [n, n]]

    figure_clouds(sources[0], targets[0]).savefig("test.png")


# test_plots()


def test_otdPW_plot():
    source = create_sphere(n)[0]  # 0 element is the pointcloud
    target = create_sphere(n)[0] + 1  # 0 element is the pointcloud
    target_2 = create_sphere(n)[0] + 2  # 0 element is the pointcloud

    otdPW = OTDPairwise([source], [target, target_2])
    otdPW.plot().savefig("removeme_test_otdPW_plot.png")
    otdPW.plot(0, 1).savefig("removeme_test_otdPW_plot_target2.png")


def test_otdPW_plot_brenier():
    source = create_sphere(10)[0]  # 0 element is the pointcloud
    target = create_sphere(10)[0] + 1  # 0 element is the pointcloud
    target_2 = create_sphere(10)[0] + 2  # 0 element is the pointcloud

    otdPW = OTDPairwise([source], [target, target_2])
    otdPW.compute()
    otdPW.plot_brenier().savefig("removeme_test_otdPW_plot_bernier.png")
    otdPW.plot_brenier(0, 1).savefig("removeme_test_otdPW_plot_bernier_target2.png")


# test_otdPW_plot_brenier()


def test_otdPW_plot_brenier_randomness():
    from torch import manual_seed, rand

    source = create_sphere(10)[0]  # 0 element is the pointcloud
    manual_seed(3481)
    random_noise = rand(source.shape)
    otdPW = OTDPairwise([source], [source + 2 + random_noise.to(source.device) * 0.25])
    otdPW.compute()
    otdPW.plot_brenier().savefig("removeme_test_otdPW_plot_bernier_randomness.png")


def test_otdPW_plot_brenier_different_n():
    source = create_sphere(10)[0]  # 0 element is the pointcloud
    target_5 = create_sphere(5)[0] + 2  # 0 element is the pointcloud
    target_15 = create_sphere(15)[0] + 2  # 0 element is the pointcloud
    otdPW = OTDPairwise([source], [target_5, target_15])
    otdPW.compute()
    otdPW.plot_brenier(0, 0).savefig("removeme_test_otdPW_plot_bernier_n10.5.png")
    otdPW.plot_brenier(0, 1).savefig("removeme_test_otdPW_plot_bernier_n10.15.png")


# def test_umap():
#     source = create_sphere(10)[0]  # 0 element is the pointcloud
#     target_10 = create_sphere(10)[0] + 2  # 0 element is the pointcloud

#     otdPW = OTDPairwise([source], [target_10])
#     otdPW.compute()
#     otdPW.plot_umap().savefig("removeme_test_otdPW_plot_umap.png")
