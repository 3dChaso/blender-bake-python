import os
import ctypes
import subprocess
def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        # 如果当前用户已经是管理员，则直接返回True
        return True
    else:
        return False
def Write_OS_Var():#写全局变量
    if not run_as_admin():
        print("请以管理员身份运行该程序！")
    else:
        bakePath = "D:\\bakeTemp\\"
        subprocess.call(["setx", "bakeTemp", bakePath])
        print("全局变量写入完毕,请重启程序")   
    
def read_OS_Var():#读取全局变量
    global path_value
    if not run_as_admin():
        print("请以管理员身份运行该程序！")
    else:
        path_value = os.getenv('bakeTemp')
        if path_value != None:
            print("读取全局变量成功-bakeTemp:", path_value)
            return True
        else:
            return False
             
def try_read_OS_Var():
    if not read_OS_Var():#失败，写入一次
        Write_OS_Var()
        return None
    else:
        return path_value