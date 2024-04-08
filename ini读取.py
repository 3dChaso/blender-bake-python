import os
import ctypes
import sys

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        # 如果当前用户已经是管理员，则直接返回True
        path_value = os.getenv('baketemp')
        print("baketemp:", path_value)
        return True
    else:
        # 否则，使用ShellExecute来请求管理员权限
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return False


if not run_as_admin():
        print("请以管理员身份运行该程序！")