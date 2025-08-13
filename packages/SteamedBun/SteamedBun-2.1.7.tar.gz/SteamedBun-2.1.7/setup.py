"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: setup.py
@Time: 2025/01/23 23:36
"""

from setuptools import find_packages
from setuptools import setup

__version__ = "2.1.7"

# 包目录下资源
PackageData = [
    "font/song.ttc",
    "browser_session.yaml",
    "config.ini"
]

# 依赖的三方库
DependentPackage = [
    "allure-pytest==2.13.2",
    "colorama==0.4.6",
    "NumPy==1.23.5",
    "openpyxl==3.1.0",
    "pandas>=2.0.3",
    "Pillow==9.5.0",
    "playwright==1.44.0",
    "pymysql==1.1.1",
    "python-dateutil==2.8.2",
    "pytest==7.3.2",
    "pytest-ordering==0.6",
    "pytest-xdist==3.5.0",
    "PyYAML==6.0",
    "requests==2.30.0",
    "retry==0.9.2",
    "selenium==4.4.3",
    "setuptools<=60.2.0",
    "SteamedBun-Uninstall==1.0.0",
    "urllib3==1.26.12"
]

setup(
    name="SteamedBun",
    author="馒头",
    author_email="neihanshenshou@163.com",
    description="馒头的第三方库",
    long_description=open(file="README.md", encoding="utf-8", mode="r").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={"": PackageData},
    version=__version__,
    install_requires=DependentPackage,
    license="Apache License 2.0",
    license_file="LICENSE",
    platforms=["MacOS、Window"],
    fullname="馒头大人",
    url="https://github.com/neihanshenshou/SteamedBun",
    python_requires=">=3.5",  # 支持的Python版本范围
)
