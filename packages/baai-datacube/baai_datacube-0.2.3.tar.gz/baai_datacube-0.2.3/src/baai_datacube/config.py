import time
import os
import pathlib
import threading
import json

import jwt
import requests


DATACUBE_HOME = pathlib.Path(os.path.expanduser("~")) / ".cache" / "datacube"
DATACUBE_HOME.parent.mkdir(parents=True, exist_ok=True)

REQUEST_HEADER = {
    "Accept-Language": "zh-CN",
    "Content-Type": "application/json",
}

class Application:
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> "Application":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance # noqa

    def __init__(self, dataset_id: str="",  save_path=".", meta_path="", jobs=8, host: str = " http://datacube.baai.ac.cn/api"):
        if not self._initialized:

            self.root_path = DATACUBE_HOME
            self.req_header = REQUEST_HEADER
            self.req_host =  host
            self.sign_api = f"{host}/storage/sign-generate"
            self.login_api = f"{host}/auth/user-access-key-login"
            self.logger_api = f"{host}/logger/download/create"

            self.dataset_id = dataset_id # 下载的数据集
            self.save_path = save_path
            self.mate_path = meta_path
            self.chunk_size = 1024 * 1024 * 5
            self.jobs = jobs

            self._login_token = ""
            self._login_lock = threading.Lock()

            self._initialized = True

    def try_access_token(self):
        save_name = self.root_path / "config.json"

        with open(save_name, "r") as fr:
            data = json.loads(fr.read())
        resp_login = requests.post(self.login_api, json={"accessKey": data.get("access_key"), "secretKey": data.get("secret_key")}, headers=self.req_header)

        return resp_login.json().get("data").get("token")

    def update_token(self):
        self._login_lock.acquire()
        self._login_token = self.try_access_token()
    def try_login(self):
        if self._login_token == "":
            self.update_token()
        decoded = jwt.decode(self._login_token, options={"verify_signature": False})
        exp = decoded.get("exp")
        if exp + 60 * 10 < int(time.time()):
            self.update_token()
        return self._login_token


class Progress:
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> "Application":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance # noqa

    def __init__(self):
        if not self._initialized:
            self._lock = threading.Lock()
            self.require_count = 0 # 需要下载的数量
            self.require_size = 0 # 需要下载的大小

            self.download_count = 0 # 下载数量
            self.download_size = 0 # 下载大小

            # 失败数量
            self.fail_count = 0

            self._initialized = True

    def add_require_count(self, count):
        with self._lock:
            self.require_count += count

    def add_require_size(self, size):
        with self._lock:
            self.require_size += size

    def add_download_count(self, count):
        with self._lock:
            self.download_count += count

    def add_download_size(self, size):
        with self._lock:
            self.download_size += size

    def add_fail_count(self, count):
        with self._lock:
            self.fail_count += count