import time
from tqdm import tqdm

def dataset_download(dataset_id, save_path, meta_path, jobs=8):

    from .config import Application, Progress
    from .baai_logger import logger_download

    save_path = save_path.strip().rstrip("/")
    app = Application(dataset_id, save_path, meta_path, jobs=jobs)
    app.try_login()

    progress = Progress()
    logger_download()


    from .baai_downloder import executor_spawn, download_progress, download_readrows, download_watch


    p1 = executor_spawn.submit(download_readrows)
    p2 = executor_spawn.submit(download_progress)
    p3 = executor_spawn.submit(download_watch)

    with tqdm(
        desc="speed",
        # colour="green",
        ncols=100,
        ascii="░▒▓█",
        unit="B",
        unit_scale=True,
        # bar_format="{desc}: {percentage:3.1f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}",
        bar_format="[{elapsed}] | {percentage:3.1f}%|{bar}| {n_fmt}/{total_fmt}{postfix} [{desc}: {rate_fmt}]"
    ) as pbar:
        last_size = 0
        while True:
            time.sleep(1)
            # 更新总任务数
            pbar.total = progress.require_size
            pbar.refresh()  # 刷新以显示新的total

            # 计算增量并更新进度条
            current_size = progress.download_size
            increment = min(current_size, progress.require_size) - last_size

            if increment > 0:
                pbar.update(increment)
                last_size = current_size

            pbar.set_postfix({
                "count": f"{progress.download_count}/{progress.require_count}",
            })

            if progress.require_size == progress.download_size and progress.require_count == progress.download_count:
                break

    p1.result()
    p2.result()
    p3.result()

    logger_download()