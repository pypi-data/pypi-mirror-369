#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/27 11:35
# @Author  : yaitza
# @Email   : yaitza@foxmail.com

import requests

from dg_itest.utils.logger import logger, allure_log
from dg_itest import host_url

class DgRequests(object):
	def __init__(self):
		self.server_url = host_url

	@allure_log
	def http_request(self, method, url, headers=None, **kwargs):
		"""
		针对接口封装.
		"""
		method = method.upper()

		request_headers = {'finger': 'auto_test'}
		if headers is not None:
			request_headers.update(headers)
		# logger.info(f'inputs params: {str(kwargs)}')
		result = requests.request(method, url=self.server_url + url, headers=request_headers, **kwargs)
		# logger.info(f'response: {str(result.json())}')
		return result
