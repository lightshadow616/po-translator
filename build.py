import os
import sys
from pathlib import Path
import PyInstaller.__main__

def build_exe():
    # 获取项目根目录
    project_dir = Path(__file__).parent
    
    # 定义打包参数
    args = [
        'main.py',  # 主脚本
        '--name=po-translator',  # 生成的exe名称
        '--onedir',  # 打包成单个目录
        '--noconsole',  # 不显示控制台窗口（如果需要控制台输出可以移除这个参数）
        '--add-data=.env.example;.',  # 添加示例.env文件
        '--hidden-import=openai',
        '--hidden-import=polib',
        '--hidden-import=python-dotenv',
        '--collect-data=python-dotenv',  # 正确收集dotenv数据
        '--exclude-module=tkinter',  # 排除不需要的模块
        '--exclude-module=matplotlib',
        '--exclude-module=PIL',
        '--collect-data=python-dotenv',  # 正确收集dotenv数据
        '--distpath=dist',  # 输出目录
        '--workpath=build',  # 工作目录
        '--specpath=.',  # spec文件目录
        '--clean',  # 打包前清理
        '--noconfirm',  # 覆盖输出目录而不提示
    ]
    
    # 执行打包
    PyInstaller.__main__.run(args)
    
    print("打包完成！")
    print("生成的exe文件在dist/po-translator目录中")
    print("请确保在运行exe文件的同级目录下放置.env配置文件")
    print("可以将 .env.example 重命名为 .env 并修改相应配置")

if __name__ == "__main__":
    build_exe()