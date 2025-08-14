from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    return ""

# 读取requirements.txt
def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

setup(
    name="python-sbx",
    version="1.0.0", # 版本号
    author="eooce",  # 作者名
    author_email="eooce@outlook.com",  # 作者邮箱
    description="Sing-box",  # 简短描述
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/eooce/Sing-box",  # 项目URL
    py_modules=["app"],  # 使用py_modules而不是packages
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "python-sbx=app:main",  # 命令行入口点
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
