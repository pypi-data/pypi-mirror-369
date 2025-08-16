#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/19 18:58
# @Author  : yaitza
# @Email   : yaitza@foxmail.com
import yaml


class YamlHandler():
	def __init__(self, file_path):
		self.file_path = file_path

	def load(self):
		with open(self.file_path, 'r', encoding='utf-8') as f:
			raw = yaml.safe_load(f.read())
		return raw