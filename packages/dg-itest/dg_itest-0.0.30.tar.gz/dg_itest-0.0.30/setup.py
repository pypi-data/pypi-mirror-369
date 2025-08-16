#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/20 11:17
# @Author  : yaitza
# @Email   : yaitza@foxmail.com

import os
from setuptools import setup, find_packages

def get_requirements():
    requirements = 'requirements.txt'
    if not os.path.exists(requirements):  # install from tar
        requirements = 'dg_itest.egg-info/requires.txt'
    with open(requirements) as fp:
        install_requires = fp.read()
    return install_requires.split('\n')

with open("README.md", mode='r', encoding="utf-8") as f:
    readme = f.read()

setup(name='dg_itest',
      version='0.0.30',
      description='接口自动化测试框架',
      long_description=readme,
      long_description_content_type="text/markdown",
      url='https://github.com/yaitza/dg-itest',
      download_url='https://github.com/yaitza/dg-itest/releases',
      author='yaitza',
      author_email='yaitza@foxmail.com',
      packages=find_packages(),
      package_data={'': ['*.py']},
      install_requires=get_requirements(),
      zip_safe=False)