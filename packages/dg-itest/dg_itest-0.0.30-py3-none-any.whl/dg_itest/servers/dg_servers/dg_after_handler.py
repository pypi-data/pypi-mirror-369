#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/3/11 11:29
# @Author  : 杨智杰
# @Email   : yangzhijie@datagrand.com
import json
import time
import jsonschema
import jsonpath
import pytest

from dg_itest.utils.logger import log_attach
from dg_itest.utils.diff_helper import DiffHelper
from dg_itest.utils.cache import local_cache

class DgAfterHandler:
	def __init__(self):
		pass

	# todo 断言类型需要增加，目前只支持eq(相等), co(包含), sa(存储), wa(等待时长), inn(非空判断)。
	def after(self, in_params, response):
		"""
		对接口返回值进行各种后处理操作：断言，提取值，判断包含
		in_params: 传入的参数，格式为json
		response: 接口返回的http响应
		"""
		validate = in_params.get("validate")
		expect = in_params.get('expect')
		for item in validate:
			if "js" in item.keys() or "jsonschema" in item.keys():
				# json schema 校验对应返回接口的数据结构
				self._jsonschema(item, response)
			if "sa" in item.keys() or "save" in item.keys():
				# sa 关键字，存储用例的值供后续接口作为入参使用
				self._save(item, response)
			if "eq" in item.keys() or "equal" in item.keys():
				self._equal(item, response, expect)
			if "co" in item.keys() or "contains" in item.keys():
				self._contains(item, response, expect)
			if "wa" in item.keys() or "wait" in item.keys():
				start_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
				time.sleep(item.get("wa"))
				end_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
				log_attach(f'waite {item.get("wa")}s, from {start_time} to {end_time}', name=f'wait {item.get("wa")}s')
			if "inn" in item.keys() or "isNotNull" in item.keys():
				self._is_not_null(item, response)

	def _jsonschema(self, item, response):
		"""
		接口返回json数据的数据结构进行JSON Schema校验
		item: 单个用例的入参
		response: 接口返回的http响应
		"""
		json_schema = item.get("js") if "js" in item.keys() else item.get("jsonschema")
		actual_result = response.json()
		try:
			jsonschema.validate(actual_result, json_schema)
			log_attach(
				f'JSON Schema: {json_schema} ,\n\nactual_result: {actual_result}',
				name=f'SON Schema check: passed')
		except jsonschema.ValidationError as e:
			log_attach(
				f'JSON Schema: {json_schema} ,\n\nactual_result: {actual_result}',
				name=f'JSON Schema assert: failed')
			pytest.fail(f'JSON Schema check failed：{e}')


	def _equal(self, item, response, expect):
		"""
		接口返回的值和期望值一致性校验
		item: 单个用例的入参
		response: 接口返回的http响应
		expect：用例执行的期望值
		"""
		validate_rule = item.get("eq") if "eq" in item.keys() else item.get("equal")
		actual_result = jsonpath.jsonpath(response.json(), validate_rule)
		expect_result = jsonpath.jsonpath(expect.get('json'), validate_rule)

		if isinstance(actual_result, list) and isinstance(expect_result, list):
			actual_result = sorted(actual_result)
			expect_result = sorted(expect_result)
		# assert actual_result == expect_result, '\n' + DiffHelper.diff(str(actual_result), str(expect_result))
		if actual_result != expect_result:
			log_attach(
				f'validate_rule: {validate_rule}\nactual_result: {actual_result}\nexpect_result: {expect_result}',
				name=f'equal assert: failed')
			pytest.fail('\n' + DiffHelper.diff(str(actual_result), str(expect_result)))
		else:
			log_attach(
				f'validate_rule: {validate_rule}\nactual_result: {actual_result}\nexpect_result: {expect_result}',
				name=f'equal assert: passed')

	def _contains(self, item, response, expect):
		"""
		判断接口返回的值是否包含期望值或期望值包含接口返回的值
		item: 单个用例的入参
		response: 接口返回的http响应
		expect：用例执行的期望值
		"""
		contains_rule = item.get('co') if 'co' in item.keys() else item.get('contains')
		actual_result = jsonpath.jsonpath(response.json(), contains_rule)
		expect_result = expect.get('contains')
		# assert expect_result in json.dumps(actual_result, ensure_ascii=False), f'{expect_result} not in {actual_result}'
		if expect_result not in json.dumps(actual_result, ensure_ascii=False) and actual_result[0] not in expect_result:
			log_attach(
				f'nvalidate_rule: {contains_rule} ,\nactual_result: {actual_result}\nexpect_result: {expect_result}',
				name='contains assert: failed')

			pytest.fail(f'\nexpect: {expect_result} \nnot in\nactual: {actual_result}\n\nactual: {actual_result} \nnot in\nexpect: {expect_result}')
		else:
			log_attach(
				f'validate_rule: {contains_rule} ,\nactual_result: {actual_result}\nexpect_result: {expect_result}',
				name='contains assert: passed')

	def _save(self, item, response):
		"""
		接口返回的值存在在给定的变量中
		item: 单个用例的入参
		response: 接口返回的http响应
		"""
		sa_value = item.get("sa") if "sa" in item.keys() else item.get("save")
		for sa_item_key in sa_value.keys():
			sa_item_value = jsonpath.jsonpath(response.json(), sa_value.get(sa_item_key))
			assert type(sa_item_value) is list and len(sa_item_value) > 0, '\n' + '未获取到值'
			sa_item_keep_value = eval(f'{item.get("convert")}({sa_item_value[0]})') if item.get("convert") else sa_item_value[0]
			log_attach(f'${sa_item_key}$:{sa_item_keep_value}\tcache type: {str(type(sa_item_keep_value))}', name='save local cache')
			local_cache.put(f"${sa_item_key}$", sa_item_keep_value)

	def _is_not_null(self, item, response):
		"""
		判断接口返回的值是否不为空，为空用例失败
		item: 单个用例额入参
		response: 接口返回的http响应
		"""
		validate_rule = item.get("inn") if "inn" in item.keys() else item.get("isNotNull")
		actual_result = jsonpath.jsonpath(response.json(), validate_rule)

		if actual_result == "" or actual_result is None:
			log_attach(f'{validate_rule}\nactual_result: {actual_result}\n',
					   name='is not null assert: failed')

			pytest.fail('\n' + str(actual_result) + "is null or empty")
		else:
			log_attach(f'{validate_rule}\nactual_result: {actual_result}\n',
					   name='is not null assert: passed')

	def check_status(self, in_params):
		"""
        校验接口返回状态
        由于接口存在异步执行，返回对应状态耗时较长，通过其状态校验，多次循环执行得到正确实际状态
        :return: 返回状态
        """
		status = True
		for item in in_params.get("validate"):
			if 'cs' in item.keys():
				cs_value = item.get('cs')
				for cs_item_key in cs_value.keys():
					status = status and local_cache[f"${cs_item_key}$"] == cs_value.get(cs_item_key)
		return status
