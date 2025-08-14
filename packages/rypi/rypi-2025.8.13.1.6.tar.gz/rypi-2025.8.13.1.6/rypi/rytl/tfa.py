INFO = '''
tfa: 获取双重因素认证(2FA(Two Factor Authentication))动态验证码
本工具是用 pyotp 根据指定的密钥生成动态验证码
用来生成动态验证码的密钥, 通常由网络应用服务商提供
本工具有两个用途：
1. 生成一次性动态验证码: rypi rytl tfa key
2. 生成密钥, 用于生成动态验证码, 该用途适用应用服务商: rypi rytl tfa -k
'''

HELP = '''
+-------------------------------------------+
|             tfa: get 2FA code             |
+-------------------------------------------+
|            HomePage: rymaa.cn             |
+-------------------------------------------+

Usage:
    rypi rytl tfa [option]

Options:
    -H, --help   Show help / 显示帮助
    -I, --info   Show info / 显示信息
    -V, --version   Show version / 显示版本
    -k, --key   Generate key / 生成密钥, 该密钥用于生成动态验证码
'''

##############################

import pyotp
import argparse

##############################

VER = '\ntfa version: 2025.8.1.1.0'

def help():
    print(HELP)

def info():
    print(INFO)

def main(*args):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('option', nargs='?')
    parser.add_argument('-H', '--help', action='store_true')
    parser.add_argument('-I', '--info', action='store_true')
    parser.add_argument('-V', '--version', action='store_true')
    parser.add_argument('-k', '--key', action='store_true')

    args = parser.parse_args()
    
    if args.info:
        info()
    elif args.version:
        print(VER)
    elif args.key:
        otp = pyotp.random_base32()
        print('\n')
        print(otp)
    elif args.option:
        otp = pyotp.TOTP(args.option)
        print('\n')
        print(otp.now())
    else:
        help()

if __name__ == '__main__':
    main()