import uuid
import requests


process_id = uuid.uuid4().__str__().replace("-", "")[:32]

def logger_download():
    from .config import  Application, Progress

    app = Application()
    app.try_login()

    headers = {
        "Authorization": f"Bearer {app.try_login()}",
    }
    progress = Progress()
    headers.update(app.req_header)
    post_data = {"datasetId": app.dataset_id, "progressId": process_id, "downloadSize": progress.download_size}

    _resp = requests.post(app.logger_api, json=post_data,headers=headers)
