INFO = '''
锐派(RyPi): 是 锐白 开发的 派神(python) 工具包, 包含以下网络工具: 
锐网(RyNet): 一个网络服务器管理工具, 后端程序: Faskapi + Uvicorn + Nginx + ArangoDB + SeaWeedFS
锐通(RyTl): 通用(Util)函数/工具库
锐鸥(RyO): 一个网站工具, 包含前端与后端程序, 后端开发语言: 派神(python)
锐代(RyDy): 一个网络数据抓包代理工具
锐辅(RyFu): 一个辅助工具, 可用于执行日常自动任务, 如: 游戏辅助, 广告辅助, 应用辅助
锐爬(RyPa): 一个网络内容爬取工具, 如新闻内容, 电影内容, 电商内容
锐库(RyKu): 一个简易数据库
锐窗(RyWin): 用 派神(python) 开发的 锐派(RyPi) 图形窗口，方便在图形界面系统(PyQt)或终端(Urwid)进行图形可视化操作

更多内容请前往 锐码 官网查阅: rymaa.cn
作者: 锐白
主页: rybby.cn, ry.rymaa.cn
邮箱: rybby@163.com
'''

HELP = '''
+-------------------------------------------+
|        RyPi: Rybby's Python Tools         |
+-------------------------------------------+
|            HomePage: rymaa.cn             |
+-------------------------------------------+

Usage:
    rypi [option]

Options:
    -h, --help   Show help / 显示帮助
    -i, --info   Show info / 显示信息
    -v, --version   Show version / 显示版本
'''

##############################

import sys
import argparse
from __init__ import __version__ as VER
import comm
import conf

##############################

def help():
    print(HELP)

def info():
    print(INFO)

def main(*args):
    # 主解析器
    parser = argparse.ArgumentParser(add_help=False)
    subp = parser.add_subparsers(dest='smod', required=False)  # 子模块解析器

    # 全局选项
    parser.add_argument('-H', '--help', action='store_true')
    parser.add_argument('-I', '--info', action='store_true')
    parser.add_argument('-V', '--version', action='store_true')

    # 定义子模块（如 rynet、rytl 等）
    for m in conf.MODS:
        mp = subp.add_parser(m)
        mp.add_argument('options', nargs='*', help=f'{m} 子模块的参数')

    args = parser.parse_args()

    # 处理全局选项
    if args.help:
        help()
    elif args.info:
        info()
    elif args.version:
        print(f'\nRyPi Version: {VER}')
    # 处理子模块
    elif args.smod in conf.MODS:
        print(f"执行子模块: {args.smod}, 参数: {args.options}")
        # 调用子模块：
        md = comm.load(f'{args.smod}.main')
        #md = comm.load(args.smod)
        print(md.main)
        md.main(args.options)
    else:
        help()

if __name__ == '__main__':
    main()