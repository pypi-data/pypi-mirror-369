import sys
import os

def add_to_sys_path(abs_path, rel_tool_path):
    """
    将根据相对工具路径和绝对路径拼接得到的新绝对路径添加到 sys.path 中。

    参数:
    abs_path (str): 绝对路径字符串。
    rel_tool_path (str): 相对工具路径字符串。

    返回:
    无 - 此函数直接修改 sys.path 列表。
    """

    # 获取rel_tool_path中的第一个文件夹
    first_folder = os.path.normpath(rel_tool_path).split(os.sep)[0]
    # 查找first_folder在abs_path中的位置
    index = abs_path.find(first_folder)
    if index != -1:
        # 截取abs_path中first_folder之前的部分
        prefix = abs_path[:index]
        # 拼接成新的绝对路径
        new_abs_path = os.path.join(prefix, rel_tool_path)
        
        # 将新的绝对路径添加到sys.path中
        sys.path.append(new_abs_path)