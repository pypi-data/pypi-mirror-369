#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/1 09:34
# @Author  : yaitza
# @Email   : yaitza@foxmail.com
import os
import platform
from pathlib import *
class EnvGenerater:
    """
    自动生成allure report对应Environment配置文件environment.properties.
    """

    @staticmethod
    def generate_env_file(host_url: str, file_dir: Path):
        """
        生成allure report对应Environment配置文件environment.properties.
        """
        file_name = "environment.properties"
        file_path = file_dir.joinpath(file_name)
        file = file_path.resolve()

        with(open(file=file, mode='w')) as fs:
            fs.write("测试地址=".encode("unicode_escape").decode() + host_url + '\n')
            fs.writelines("操作系统".encode("unicode_escape").decode() + "={0}".format(platform.system()) + '\n')
            fs.writelines("系统版本".encode("unicode_escape").decode() + "={0}".format(platform.version()) + '\n')
            fs.writelines("执行机名".encode("unicode_escape").decode() + "={0}".format(platform.node()) + '\n')
            fs.writelines("执行环境".encode("unicode_escape").decode() + "={0}".format(platform.python_build()))


if __name__ == "__main__":
    EnvGenerater.generate_env_file()
