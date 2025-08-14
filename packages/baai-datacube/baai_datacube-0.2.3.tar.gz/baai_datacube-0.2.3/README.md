# baai-datacube

## 数据魔方数据集下载工具

### cli
```shell
pip install baai-datacube

# 查看帮助
baai_datacube -h

# 环境信息
baai_datacube show

# 登录
baai_datacube login

# 下载
baai_datacube down --dataset=<dataset_id>
```

### python-sdk
```
# pip install baai-datacube
# baai_datacube login

from baai_datacube.downloader import dataset_download

if __name__ == "__main__":

    dataset_download(dataset_id="<dataset_id>", save_path=".")
```