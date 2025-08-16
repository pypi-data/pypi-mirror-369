#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 10:28
# @Author  : yaitza
# @Email   : yaitza@foxmail.com
import json
import time
import allure
from functools import wraps
from loguru import logger
from pathlib import Path


def init_log_config(log_dir: str, log_level):
	"""
	init log config
	:param log_dir: log locate position
	:param log_level: log show level
	:return:
	"""
	log_file_path = Path(log_dir).joinpath('{time:YYYYMMDD}.log')
	logger.add(log_file_path.absolute(),
	           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}",
	           rotation="00:00", encoding='utf-8', colorize=False, level=log_level)


def log_attach(log_data: str, name='compare_result'):
	"""
	log attach
	:param log_data:
	:return:
	"""
	logger.debug(log_data)
	allure.attach(log_data, name=name)


def allure_log(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		try:
			start = 1000 * time.time()
			logger.debug(f"========================  Begin: {func.__name__}  =================================")
			logger.debug(str(kwargs))
			allure.attach(str(kwargs), name='kwargs')
			result = func(*args, **kwargs)

			if hasattr(result, 'json'):
				logger.debug(str(result.json()))
				allure.attach(json.dumps(result.json(), sort_keys=True, indent=4, separators=(',', ':')).encode().decode("unicode_escape"), name='response')
			else:
				logger.debug(str(result))
				allure.attach(str(result).encode().decode("unicode_escape"), name='response')
			end = 1000 * time.time()
			logger.debug(f"=============   End: {func.__name__}; cost time: {end - start}ms   =============")
			return result
		except Exception as e:
			logger.error(repr(e))
			raise e

	return wrapper
