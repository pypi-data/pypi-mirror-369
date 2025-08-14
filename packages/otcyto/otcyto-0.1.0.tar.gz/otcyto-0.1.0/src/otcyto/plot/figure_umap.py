# import umap
# from matplotlib import pyplot as plt
# import torch
# from otcyto.plot.figure_clouds import figure_clouds


# def figure_umap(
#     source_pointcloud,
#     target_pointcloud,
#     x_i: int = 0,
#     y_i: int = 1,
#     map_source_to_target: torch.Tensor = None,
#     n_neighbors=10,
#     min_dist=0.1,
#     metric="euclidean",
#     *args,
#     **kwargs,
# ) -> plt.Figure:
#     # 1. Calculate UMAP on source pointcloud
#     reducer = umap.UMAP(
#         n_neighbors=n_neighbors,
#         min_dist=min_dist,
#         n_components=2,
#         metric=metric,
#         *args,
#         **kwargs,
#     )
#     umap_transform = reducer.fit(source_pointcloud)
#     # 2. Apply UMAP to target pointcloud
#     source_embedding = umap_transform.embedding_
#     target_embedding = umap_transform.transform(target_pointcloud)
#     map_source_to_target_embedded = umap_transform.transform(map_source_to_target)
#     raise NotImplementedError("I am unsure if 'map_source_to_target_embedded - source_embedding' is actually correct")
#     fig = figure_clouds(
#         source_embedding,
#         target_embedding,
#         map_source_to_target=map_source_to_target_embedded - source_embedding,
#     )
#     return fig
