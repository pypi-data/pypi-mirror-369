import pathlib

from .baai_download import dataset_download as download_dataset
from .baai_meta import download_meta


def dataset_download(dataset_id, save_path="."):

    save_path = pathlib.Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)
    print("---- download ----")

    meta_path = save_path / f"{dataset_id}.bin"
    if not meta_path.exists():
        dataset_meta = download_meta(dataset_id, host="https://datacube.baai.ac.cn/api")

        with open(meta_path, "w") as f:
            f.write(dataset_meta)

    download_dataset(dataset_id, save_path.resolve().__str__(), meta_path.resolve().__str__())
