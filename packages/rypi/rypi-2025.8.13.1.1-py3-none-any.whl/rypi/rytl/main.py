INFO = '''
RyTl: 通用工具库
'''

HELP = '''
+-------------------------------------------+
|             RyTl: utils tools             |
+-------------------------------------------+
|            HomePage: rymaa.cn             |
+-------------------------------------------+

Usage:
    rypi rytl [option]

Options:
    -H, --help   Show help / 显示帮助
    -I, --info   Show info / 显示信息
    -V, --version   Show version / 显示版本
'''

##############################

import argparse

##############################

VER = '\nRyTl Version: 2025.8.1.1.0'

def help():
    print(HELP)

def info():
    print(INFO)

def main(*args):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-H', '--help', action='store_true')
    parser.add_argument('-I', '--info', action='store_true')
    parser.add_argument('-V', '--version', action='store_true')

    args = parser.parse_args()
    
    if args.info:
        info()
    elif args.version:
        print(VER)
    else:
        help()

if __name__ == '__main__':
    main()