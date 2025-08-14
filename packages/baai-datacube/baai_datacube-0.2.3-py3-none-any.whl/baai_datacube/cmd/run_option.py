import os
import argparse
import pathlib
import platform

import psutil

from baai_datacube.datacube_print import print_figlet


print_figlet()

version = "0.0.1"
datacube_home = pathlib.Path(os.path.expanduser("~")) / ".cache" / "datacube"
datacube_home.parent.mkdir(parents=True, exist_ok=True)

def runcmd_args():
    parser = argparse.ArgumentParser(prog='baai-datacube', description="数据魔方命令行工具")
    # 添加 --version 参数
    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
    parser.add_argument('--host', type=str, default="https://datacube.baai.ac.cn/api", help='服务地址')

    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest='command')
    show_parser = subparsers.add_parser('show', help='获取当前运行环境信息')
    show_parser.set_defaults(func=show)

    login_parser = subparsers.add_parser('login', help='登录数据魔方')
    login_parser.set_defaults(func=login)

    down_parser = subparsers.add_parser('down', help='下载数据')
    down_parser.set_defaults(func=down)
    down_parser.add_argument('--dataset', type=str, help='下载的数据集')
    down_parser.add_argument('--save-path', type=str, default=".", help='保存路径(默认当前文件夹)')
    down_parser.add_argument('--jobs', type=int, default=8, help='任务数')

    # 解析命令行参数
    cmd_args = parser.parse_args()
    if hasattr(cmd_args, 'func'):
        try:
            cmd_args.func(cmd_args)
        except Exception: # noqa
            pass
        except KeyboardInterrupt:
            print()
            pass

    else:
        parser.print_help()

def show(_cmd_args):
    import speedtest

    logical_cpus = psutil.cpu_count(logical=True)
    print(f'{platform.platform()}: {psutil.cpu_count(logical=False)}u{logical_cpus}c, {psutil.virtual_memory().total / 1024 ** 3:.0f}G')

    runtime_dir = pathlib.Path.cwd()
    print(f'pwd: {runtime_dir}')
    print(f"disk: {psutil.disk_usage(runtime_dir).total / 1024 ** 3:.0f}G")

    print("speedtest...")
    try:
        st = speedtest.Speedtest()
        download_speed = st.download()
        upload_speed = st.upload()
        print(f"ping: ↑ {upload_speed / 8_000_000:.2f} MB/s，↓ {download_speed / 8_000_000:.2f} MB/s")
    except Exception: # noqa
        # TODO: 增加国内测速方式
        pass


def login(cmd_args):
    from ..baai_login import login

    print("---- login ----")
    ak = input("请输入ak：")
    sk = input("请输入sk：")
    login(ak, sk, login_api=f"{cmd_args.host}/auth/user-access-key-login")

def down(cmd_args):
    from ..baai_meta import download_meta
    from ..baai_download import dataset_download

    save_path = pathlib.Path(cmd_args.save_path)
    save_path.mkdir(parents=True, exist_ok=True)
    print("---- download ----")

    dataset_meta = download_meta(cmd_args.dataset, host=cmd_args.host)
    meta_path = (save_path / f"{cmd_args.dataset}.bin")

    with open(meta_path, "w") as f:
        f.write(dataset_meta)

    dataset_download(
        dataset_id=cmd_args.dataset,
        save_path=save_path.resolve().__str__(),
        meta_path=meta_path.resolve().__str__(),
        jobs=cmd_args.jobs
    )

