#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/13 09:21
# @Author  : yaitza
# @Email   : yaitza@foxmail.com

from dg_itest.servers.dg_servers.dg_requests import DgRequests

class MetaSingleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None

    def __call__(self, *args, **kwargs):
        if not self.__instance:
            self.__instance = super().__call__(*args, **kwargs)
        return self.__instance


class DgSingleton(metaclass=MetaSingleton):
    apis = DgRequests()

