#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/20 16:06
# @Author  : yaitza
# @Email   : yaitza@foxmail.com

from dg_itest.servers.test_handler.test_file import *

def pytest_collect_file(parent, path):
    if path.ext in [".yml", ".xls", ".xlsx"] and path.basename.startswith("test"):
        return TestFile.from_parent(fspath=path, parent=parent)