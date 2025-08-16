#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/21 16:05
# @Author  : yaitza
# @Email   : yaitza@foxmial.com
import time
import random
import uuid


class KeyWords:
	def currenttime(self):
		"""
		获取当前时间
		:return: 当前时间, YYYYMMDDHHMMSS
		"""
		current_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
		return current_time

	def randomnum(self):
		"""
		获取随机数
		:return: 随机数, 10000-99999
		"""
		random_num = random.randint(10000, 99999)
		return str(random_num)

	def uuid4(self):
		return str(uuid.uuid4())


if __name__ == '__main__':
	change = KeyWords().randomnum()
	print(change, type(change))
	current_time = KeyWords().currenttime()
	print(current_time, type(current_time))
