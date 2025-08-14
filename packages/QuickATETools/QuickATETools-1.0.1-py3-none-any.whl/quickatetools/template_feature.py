import argparse


def main():
    parser = argparse.ArgumentParser(description='新功能的描述')
    parser.add_argument('-p', '--param', type=str, help='参数说明')
    args = parser.parse_args()

    print('这是一个新功能的空实现')
    print(f'收到的参数: {args.param}')


if __name__ == '__main__':
    main()