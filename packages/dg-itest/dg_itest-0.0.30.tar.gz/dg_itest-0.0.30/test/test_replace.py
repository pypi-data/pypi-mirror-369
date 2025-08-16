#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/21 17:02
# @Author  : yaitza
# @Email   : yaitza@foxmail.com

from dg_itest.utils.replace import Replace

def test_replace():
	pattern = r'\$.*?\$'
	source = {'test': '123', 'key': {'key1': {'key1': ['$change1$', '$change2$']}, 'key2': ['change1', 'change2']}}
	update = {'$change1$': {'key': 'source_file.png', 'value': '/data/test1.png'}, '$change2$': {'key': 'target_file.png', 'value': '/data/test1.png'}}

	result = Replace.replace_dict(pattern, source, update)
	print(result)

def test_replace_dict_key():
	update = {'$file_period_map$': 3320, '$set_date$': '2018-1-1'}
	source = {"json": {"task_id": "$financial_task_id$", "table_type": "$financial_table_type$",
	                   "template_id": "$template_id$", "file_period_map": {"$file_period_map$": ["$set_date$"]}},
	          "headers": {"Authorization": "Bearer $accessToken$"}}
	source = Replace.replace_exec(r'\$.*?\$', source, update)
