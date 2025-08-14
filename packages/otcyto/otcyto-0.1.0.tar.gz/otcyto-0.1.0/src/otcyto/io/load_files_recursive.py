from pathlib import Path

import pandas as pd
import torch


def load_files_recursive(
    data_dir: Path, verbose: bool = False, suffix: str = ".csv"
) -> tuple[list[torch.Tensor], list[str]]:
    data_dir = Path(data_dir)
    dataset: list[torch.Tensor] = []
    dataset_names: list[str] = []
    # Traverse the directory and load all the files
    for filename in data_dir.rglob(f"*{suffix}"):
        if filename.is_dir():
            continue
        if verbose:
            print(filename)
        if suffix == ".csv":
            df = pd.read_csv(filename)
            df_torch = torch.tensor(df.values)
        elif suffix == ".feather":
            df = pd.read_feather(filename)
            df_torch = torch.tensor(df.values).contiguous()
        else:
            raise NotImplementedError(f"Suffix {suffix} not implemented")
        dataset.append(df_torch)
        dataset_names.append(filename.name)
    return dataset, dataset_names
