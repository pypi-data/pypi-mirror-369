#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/19 18:55
# @Author  : yaitza
# @Email   : yaitza@foxmail.com
import traceback
from pathlib import Path
from dg_itest.utils.logger import logger
from .yaml_handler import YamlHandler
from .xlsx_handler import XlsxHandler

class FileHandler:
	def __init__(self, file_path):
		self.file_path = file_path

	def load(self):
		try:
			file = Path(self.file_path)
			if file.suffix == '.yml':
				return YamlHandler(self.file_path).load()
			elif file.suffix in [".xls", ".xlsx"]:
				return XlsxHandler(self.file_path).load()
			else:
				logger.info(f"not supported this file {self.file_path }'s suffix: {file.suffix}")
		except Exception as err:
			logger.error(traceback.print_exc())
			traceback.print_exc()




