import subprocess
from pathlib import Path


def get_filepath_filename_ext(file_url):
    """
    获取文件路径、文件名（不含扩展名）、后缀名
    :param file_url: 文件路径或 URL（字符串或 Path 对象）
    :return: (filepath: str, short_name: str, extension: str)
    """
    path = Path(file_url)
    
    filepath = str(path.parent)           # 父目录路径（字符串）
    short_name = path.stem                # 文件名（不含后缀）
    extension = path.suffix               # 扩展名（如 .txt）

    return filepath, short_name, extension



def exec_cmd(cmd_text):
    process = subprocess.Popen(cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    command_output = process.stdout.read()
    print(command_output)
    
    
if __name__ == '__main__':
    file_url = 'C:\Program Files\Tencent\Weixin\4.0.6.33\RadiumWMPF.bin'
    print(get_filepath_filename_ext(file_url))
