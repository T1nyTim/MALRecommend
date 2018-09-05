#! env/Scripts/python

from setuptools import setup, find_packages

setup(
    name='Recommend',
    version='0.0.2',
    long_description=open('README.md').read(),
	license='GPL-3.0',
    author='T1nyTim',
    author_email='',
    url='https://github.com/T1nyTim/Recommend',
    packages=find_packages(exclude=('test',)),
    install_requires=['lxml', 'requests']
)
