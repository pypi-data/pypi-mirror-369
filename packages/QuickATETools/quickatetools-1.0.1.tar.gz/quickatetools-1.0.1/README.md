# QuickATETools

一个实用的命令行工具集合，目前包含生成对角矩阵并复制到剪贴板的功能。

## 安装

```bash
pip install QuickATETools
```

## 使用方法

### 生成对角矩阵并复制到剪贴板

```bash
qate clipboardMatrix -p <矩阵大小> [-c <对角线字符>]
```

#### 参数说明
- `-p`, `--size`: 矩阵的大小（行数和列数），必填
- `-c`, `--char`: 对角线使用的字符，默认为'M'

#### 示例

生成3x3的对角矩阵（默认使用'M'）：
```bash
qate clipboardMatrix -p 3
```

生成的矩阵：
```
M00
0M0
00M
```

生成4x4的对角矩阵，使用'X'作为对角线字符：
```bash
qate clipboardMatrix -p 4 -c X
```

生成的矩阵：
```
X000
0X00
00X0
000X
```

### 模板功能

这是一个新功能的空实现，用于展示如何扩展工具集。

```bash
qate templateFeature [-p <参数>]
```

#### 参数说明
- `-p`, `--param`: 参数说明

## 待开发功能
- 完善模板功能的具体实现
- 更多实用的命令行工具