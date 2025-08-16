#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/20 10:21
# @Author  : yaitza
# @Email   : yaitza@foxmail.com

import difflib


class DiffHelper:
    """
    比较差异
    """
    @staticmethod
    def diff(source, target):
        if isinstance(source, str) and isinstance(target, str):
            differ = difflib.Differ()
            str_diff = differ.compare(source.splitlines(), target.splitlines())
            return '\n'.join(list(str_diff))

    def _diff_dict(self, source: dict, target: dict):
        """
        对比dict的差异
        """
        differ = set(source.items()) ^ set(target.items())
        return differ
