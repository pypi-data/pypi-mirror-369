import argparse
import pyperclip

def generate_diagonal_matrix(size, diagonal_char='M'):
    """生成指定大小的对角矩阵

    Args:
        size (int): 矩阵的行数和列数
        diagonal_char (str): 对角线使用的字符

    Returns:
        str: 生成的对角矩阵字符串
    """
    matrix = []
    for i in range(size):
        row = []
        for j in range(size):
            if i == j:
                row.append(diagonal_char)
            else:
                row.append('0')
        matrix.append(''.join(row))
    return '\n'.join(matrix)


def main():
    parser = argparse.ArgumentParser(description='生成对角矩阵并复制到剪贴板')
    parser.add_argument('-p', '--size', type=int, required=True, help='矩阵的大小（行数和列数）')
    parser.add_argument('-c', '--char', type=str, default='M', help='对角线使用的字符（默认为M）')
    args = parser.parse_args()

    matrix = generate_diagonal_matrix(args.size, args.char)
    pyperclip.copy(matrix)
    print(f'已将{args.size}x{args.size}的对角矩阵复制到剪贴板：')
    print(matrix)


if __name__ == '__main__':
    main()