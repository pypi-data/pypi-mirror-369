#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/3/11 17:41
# @Author  : 杨智杰
# @Email   : yangzhijie@datagrand.com

from pathlib import Path
from dg_itest import local_test_res

class FileHelper:

	@staticmethod
	def replace_file_to_stream(files_array):
		"""
        替换文件为文件流
        """
		all_resource_files = Path(local_test_res).rglob("*.*")
		files_buffer = []
		for file_name in files_array:
			file = [file_item for file_item in all_resource_files if file_item.name == file_name]
			if len(file) > 0:
				suffix = file[0].suffix
				if suffix in ['.jpg', '.jpeg', '.png']:
					content_type = f'image/{suffix.lstrip(".")}'
				elif suffix in ['.pdf']:
					content_type = f'application/{suffix.lstrip(".")}'
				elif suffix in ['.xlsx']:
					content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
				elif suffix in ['.xls']:
					content_type = 'application/vnd.ms-excel'
				else:
					content_type = '*/*'

				files_buffer.append(('file', (file_name, open(file[0].resolve(), 'rb'), content_type)))
			else:
				continue
		return files_buffer