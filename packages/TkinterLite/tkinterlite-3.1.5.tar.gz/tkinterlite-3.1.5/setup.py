import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="TkinterLite",  # Easy Tkinter
    version="3.1.5",
    packages=find_packages(),
    install_requires=requirements,
    author="YanXinle",
    author_email="1020121123@qq.com",
    description="tkinter库的简化版",
    url="https://github.com/Yanxinle1123/LeleEasyTkinter",
)
