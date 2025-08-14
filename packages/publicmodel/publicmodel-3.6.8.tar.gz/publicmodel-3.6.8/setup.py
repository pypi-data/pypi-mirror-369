from setuptools import setup, find_packages

setup(
    name="publicmodel",
    version="3.6.8",
    packages=find_packages(),
    install_requires=[
        'qrcode~=8.2',
        'pillow~=11.3.0',
        'colored~=2.3.1',
        'opencv-python~=4.12.0.88',
        'requests~=2.32.4',
        'bs4~=0.0.2',
        'beautifulsoup4~=4.13.4',
        'googletrans~=4.0.2',
        'pytest~=8.4.1',
    ],
    author="YanXinle",
    author_email="1020121123@qq.com",
    description="作者: YanXinle",
    url="https://github.com/Yanxinle1123/LeleComm",
)
