# MWE for `otcyto`
The following code snippet provides a minimal working example (MWE) for using the `otcyto` package to compute optimal transport distances between synthetic point clouds, plot the results, and visualize the Brenier map.
```python
    from otcyto.geomloss.create_sphere import create_sphere
    from otcyto.otd_pairwise import OTDPairwise
    from otcyto.plot.figure_clouds import figure_clouds

    # Create synthetic point clouds
    n = 1_000
    source = create_sphere(n)[0]
    target_1 = create_sphere(n)[0] + 1
    target_2 = create_sphere(n)[0] + 2

    # Compute pairwise OTD
    otd = OTDPairwise([source], [target_1, target_2])
    otd.compute()

    # Inspect results
    print(otd.otd_df)

    # Plot and save OTD matrix
    otd.plot().savefig("otd_matrix.png")

    # Optional: plot Brenier map for first target
    otd.plot_brenier(0, 0).savefig("brenier_map.png")

    # Overlay point clouds
    figure_clouds(source, target_1).savefig("clouds.png")
```
