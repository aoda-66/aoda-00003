import subprocess
import sys
import os

PYTHON_EXE = r"C:\Python314\python.exe"

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 50)
    print("文博文物数字化管理系统 - 启动脚本")
    print("=" * 50)
    print()
    
    print("1. 初始化数据库和权限...")
    result = subprocess.run([PYTHON_EXE, "-m", "app.initial_data"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("错误:", result.stderr)
    print()
    
    print("2. 启动API服务...")
    print("服务地址: http://0.0.0.0:8000")
    print("API文档: http://0.0.0.0:8000/docs")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    print()
    
    subprocess.run([PYTHON_EXE, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    main()