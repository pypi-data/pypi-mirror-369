#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/19 18:25
# @Author  : yaitza
# @Email   : yaitza@foxmail.com
import json
import time
import allure
import pytest
import traceback
from dg_itest import local_test_loop_times
from dg_itest.utils.logger import logger, log_attach
from dg_itest.servers.dg_servers.dg_singleton import DgSingleton
from dg_itest.servers.dg_servers.dg_after_handler import DgAfterHandler
from dg_itest.utils.replace import Replace
from dg_itest.utils.file_helper import FileHelper
class TestItem(pytest.Item):
    def __init__(self, name, parent, values):
        super(TestItem, self).__init__(name, parent)
        self.name = name
        self.values = values

    def runtest(self):
        logger.info(f'execute case: {self.name}; url: {self.values.get("request").get("url")}')
        request_data = self.replace(self.values['request'])
        params = request_data.get("params")
        if "files" in params.keys():
            params.update({"files": FileHelper.replace_file_to_stream(params.get("files"))})
        request_data.pop("params")
        request_data.update(params)
        exec_flag, exec_count = False, 0
        try: # 此处不应该捕获异常，否则pytest无法判断用例failed
            while exec_count < local_test_loop_times and not exec_flag :  # 异步任务，轮询执行local_test_loop_times次保证完成后进行校验
                api = DgSingleton().apis
                response = api.http_request(**request_data)
                DgAfterHandler().after(self.values, response)
                exec_flag = DgAfterHandler().check_status(self.values)
                if exec_count > 0 or not exec_flag:
                    if exec_count <= local_test_loop_times - 2:
                        log_attach(f'休眠30秒后，开始第{exec_count + 2}循环执行中...')
                        time.sleep(30)
                    else:
                        exec_time = local_test_loop_times * 30 / 60
                        logger.error(f'用例:{self.name} 执行{exec_time}min后仍失败，请检查！')
                        log_attach(f'用例:{self.name} 执行{exec_time}min后仍失败，请检查！')
                        pytest.fail(f'用例:{self.name} 执行{exec_time}min后仍失败，请检查！')
                exec_count += 1
        except Exception:
            logger.error(traceback.format_exc())
            allure.attach(traceback.format_exc(), 'error details info')
            pytest.fail(f'用例:{self.name} 执行失败，请检查！')
            # raise Exception(f'用例:{self.name} 执行失败，请检查！')

    def replace(self, source):
        """
        替换对应参数中的${},#{}
        """
        source = Replace.replace_local_cache(source)
        source = Replace.replace_keyword(source)
        return source


