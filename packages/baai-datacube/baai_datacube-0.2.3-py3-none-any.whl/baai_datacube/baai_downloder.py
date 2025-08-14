import hashlib
import pathlib
import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import requests


from .config import Application, Progress
from .serializer import MetaData


app = Application()
progress = Progress()

executor_spawn = ThreadPoolExecutor(max_workers=10)
executor_progress = ThreadPoolExecutor(max_workers=30)
executor_sign = ThreadPoolExecutor(max_workers=10)
executor_down = ThreadPoolExecutor(max_workers=app.jobs)
executor_watch = ThreadPoolExecutor(max_workers=50)
executor_merge = ThreadPoolExecutor(max_workers=10)



def download_readrows():
    config = Application()
    with open(config.mate_path, "r") as fr:
        for _line in fr:
            progress.add_require_count(1)

def check_file(file_path: str, length: int):
    path = pathlib.Path(file_path)
    if not path.exists():
        return False
    check_size = path.stat().st_size
    return check_size== length


def download_sign(file_path: str):
    config = Application()
    req_headers = {
        "Authorization": f"Bearer {config.try_login()}",
    }
    req_headers.update(config.req_header)
    resp_sign = requests.post(config.sign_api, headers=req_headers, json={"paths": [file_path]})
    sign_addr = resp_sign.json().get("data")[0].get("endpoint")
    return sign_addr


def download_file(raw_data: str):
    config = Application()

    meta_file = MetaData(**json.loads(raw_data))

    hash_prefix = hashlib.md5(meta_file.get_storage_path().encode("utf-8")).hexdigest()
    hash_ext = pathlib.Path(meta_file.get_storage_path()).suffix

    rs_sign = executor_sign.submit(download_sign, meta_file.get_storage_path())
    sign_addr:str = rs_sign.result()
    resp_meta = requests.head(sign_addr, headers={"accept-encoding": None})
    size = int(resp_meta.headers.get('Content-Length'))

    progress.add_require_size(size)
    # 文件存在不进行下载
    if check_file(f"{config.save_path}/{hash_prefix}{hash_ext}", size):
        progress.add_download_size(size)
        progress.add_download_count(1)
        return

    chunk_size = config.chunk_size
    total_parts = int((size + chunk_size - 1) / chunk_size)

    save_path = pathlib.Path(config.save_path)
    save_path.mkdir(parents=True, exist_ok=True)

    download_futures = []
    for part_index in range(total_parts):
        start = part_index * chunk_size
        end = min(start + chunk_size, size)
        task_down = executor_down.submit(download_part_write, meta_file, start, end, hash_prefix)
        download_futures.append(task_down)

    # 等待完成
    for future in as_completed(download_futures):
        future.result()

    executor_merge.submit(download_part_merge,  hash_prefix, hash_ext, total_parts)

def download_part_write(meta_file: MetaData, start: int, end: int, part_hash):
    config = Application()

    part_idx = int(start / config.chunk_size)
    part_name =  pathlib.Path(f"{config.save_path}/{part_hash}_{part_idx}.bin")

    if check_file(part_name.__str__(),  end-start):
        pass
    else:
        range_header = f"bytes={start}-{end - 1}"
        sign_addr = download_sign(meta_file.get_storage_path())
        resp_file = requests.get(sign_addr, headers={"Range": range_header})

        # md5加密
        with part_name.open("wb") as fwriter:
            fwriter.write(resp_file.content)

    progress.add_download_size(end-start)

def download_part_merge(name_prefix, name_ext, total_parts):
    import mmap
    config = Application()
    target_path = pathlib.Path(f"{config.save_path}/{name_prefix}{name_ext}")
    with target_path.open("ab") as fwriter:
        for part_idx in range(total_parts):
            part_name = pathlib.Path(f"{config.save_path}/{name_prefix}_{part_idx}.bin")
            with part_name.open("rb") as f:
                with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
                    fwriter.write(mm)
                part_name.unlink()
    progress.add_download_count(1)


def download_progress():
    config = Application()
    with open(config.mate_path, "r") as fr:
        for _line in fr:
            try:
                executor_progress.submit(download_file, _line)
            except Exception as e: # noqa
                progress.add_download_count(-1)

def download_watch():
    import time

    while True:
        time.sleep(0.1)
        if progress.require_count == progress.download_count:
            break
    return progress.require_count




