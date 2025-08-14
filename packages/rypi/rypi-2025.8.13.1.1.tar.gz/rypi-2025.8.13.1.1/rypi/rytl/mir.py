INFO = '''
mir: 显示一些常用镜像仓库的国内链接地址
包括 pypi库和各种 linux 平台的软件仓库
'''

HELP = '''
+-------------------------------------------+
|        show pythonPkg mirror link         |
+-------------------------------------------+
|            HomePage: rymaa.cn             |
+-------------------------------------------+

Usage:
    rypi rytl mir [option]

Options:
    -H, --help   Show help / 显示帮助
    -I, --info   Show info / 显示信息
    -V, --version   Show version / 显示版本
    -p, --pypi   Show pypi mir link / 显示 pypi 库镜像链接地址
    -u, --debian   Show ubuntu,debian mir link / 显示乌班图软件镜像仓库链接地址
    -r, --redhat   Show redhat,centos mir link / 显示红帽软件镜像仓库链接地址
    -m, --macos   Show macos mir link / 显示 macos 软件镜像仓库链接地址
    -d, --docker   Show docker mir link / 显示刀客容器镜像仓库链接地址
'''

##############################

import argparse

##############################

VER = '\nmir version: 2025.8.1.1.0'

PYPI = r'''

以下国内镜像源更稳定, 按优先级推荐: 

清华源: https://pypi.tuna.tsinghua.edu.cn/simple

阿里云源: https://mirrors.aliyun.com/pypi/simple

腾讯云源: https://mirrors.cloud.tencent.com/pypi/simple

华为云源: https://repo.huaweicloud.com/repository/pypi/simple

豆瓣: https://pypi.doubanio.com/simple/

中科大: https://pypi.mirrors.ustc.edu.cn/simple/

方法 1: 临时使用镜像源

在安装包时通过 -i 参数指定镜像源: 

bash
pip install 包名 -i https://pypi.tuna.tsinghua.edu.cn/simple

方法 2: 永久修改 pip 源

Windows 系统
在用户目录下创建 pip 文件夹（如 C:\Users\你的用户名\pip）。

在文件夹内新建文件 pip.ini, 写入以下内容: 

ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
如果使用其他源, 替换 index-url 即可（如阿里云 https://mirrors.aliyun.com/pypi/simple/）。

Linux/macOS 系统

创建配置文件（当前用户生效）

bash
mkdir -p ~/.pip  # 如果目录不存在则创建
echo "[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple\ntrusted-host = pypi.tuna.tsinghua.edu.cn" > ~/.pip/pip.conf

创建全局配置文件（所有用户生效）

bash
sudo mkdir -p /etc/pip  # 确保目录存在
sudo echo "[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple\ntrusted-host = pypi.tuna.tsinghua.edu.cn" > /etc/pip.conf

方法 3: 通过命令行直接配置

运行以下命令自动修改配置: 

bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
'''

UBU = r'''

'''

RED = r'''

'''

MAC = r'''

'''

DOC = r'''

方法一: 临时使用镜像站

bash
docker run --rm -it registry.cn-hangzhou.aliyuncs.com/library/python:3.8 pip install jnius

方法二: 永久修改配置

Linux/macOS: 

bash
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "ipv6": false,
  "dns": ["1.1.1.1", "8.8.8.8"]
}
EOF
sudo systemctl restart docker

Windows: 

右键 Docker 托盘图标 → Settings → Docker Engine

添加镜像地址: 

json
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "ipv6": false,
  "dns": ["1.1.1.1", "8.8.8.8"]
}
点击 "Apply & Restart"
'''

def help():
    print(HELP)

def info():
    print(INFO)

def main(*args):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-H', '--help', action='store_true')
    parser.add_argument('-I', '--info', action='store_true')
    parser.add_argument('-V', '--version', action='store_true')
    parser.add_argument('-p', '--pypi', action='store_true')
    parser.add_argument('-u', '--ubuntu', action='store_true')
    parser.add_argument('-r', '--redhat', action='store_true')
    parser.add_argument('-m', '--macos', action='store_true')
    parser.add_argument('-d', '--docker', action='store_true')

    args = parser.parse_args()
    
    if args.info:
        info()
    elif args.version:
        print(VER)
    elif args.pypi:
        print(PYPI)
    elif args.ubuntu:
        print(UBU)
    elif args.redhat:
        print(RED)
    elif args.macos:
        print(MAC)
    elif args.docker:
        print(DOC)
    else:
        help()

if __name__ == '__main__':
    main()