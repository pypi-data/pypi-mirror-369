#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/12 17:55
# @Author  : yaitza
# @Email   : yaitza@foxmail.com

import pytest
from dg_itest.servers.file_handler.file_handler import FileHandler
from dg_itest.servers.test_handler.test_item import TestItem

class TestFile(pytest.File):
    def collect(self):
        raw = FileHandler(self.fspath).load()
        for test_case in raw:
            # 通过用例的状态判断是否执行该条用例
            if 'status' in test_case['test'].keys() and test_case['test']['status'] == 0:
                continue

            # 自动给用例编号
            if 'no' in test_case['test'].keys():
                name = str(test_case['test']['no']).zfill(len(str(len(raw)))) + '_' + test_case['test']['name']  # 拼接用例序号
            else:
                name = str(raw.index(test_case) + 1).zfill(len(str(len(raw)))) + '_' + test_case['test']['name'] # 自动拼接用例序号
            values = test_case['test']
            values.update({"name": name})
            yield TestItem.from_parent(self, name=name, values=values)



