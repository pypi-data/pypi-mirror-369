INFO = '''
常用/共用函数(Common Function)
'''

HELP = '''
+-------------------------------------------+
|           RyPi Common Functions           |
+-------------------------------------------+
|            HomePage: rymaa.cn             |
+-------------------------------------------+

Usage:
    rypi comm [option]

Options:
    -H, --help   Show help / 显示帮助
    -I, --info   Show info / 显示信息
    -V, --version   Show version / 显示版本
'''

##############################

import sys
import argparse
import importlib
import importlib.util

##############################

VER = '\ncomm version: 2025.8.1.1.0'

def load(script):
    module = importlib.import_module(script)
    return module

def loadp(path):
    name = path.replace('/', '_').replace('.', '_')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def vdump(var, indent=0):
    if isinstance(var, dict):
        print(' ' * indent + 'array({})'.format(len(var)))
        for key, value in var.items():
            print(' ' * (indent + 2) + f'[{repr(key)}] => ', end='')
            vdump(value, indent + 4)
    elif isinstance(var, list):
        print(' ' * indent + f'array({len(var)})')
        for item in var:
            print(' ' * (indent + 2) + '[{}] => '.format(var.index(item)), end='')
            vdump(item, indent + 4)
    else:
        print(f'{type(var).__name__}({repr(var)})')

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