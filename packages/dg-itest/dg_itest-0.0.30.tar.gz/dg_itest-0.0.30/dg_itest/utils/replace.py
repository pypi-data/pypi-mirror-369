#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/21 14:44
# @Author  : yaitza
# @Email   : yaitza@foxmail.com
import json
import re

import jsonpath

from dg_itest.utils.cache import local_cache
from dg_itest.utils.keywords import KeyWords


class Replace:
    @staticmethod
    def replace_local_cache(source, pattern_str=r'\$.*?\$'):
        """
        替换本地缓存中的值
        :param source: 源数据
        :param pattern_str: 匹配规则
        :return: 替换后的数据
        """
        source_str = json.dumps(source)
        pattern = re.compile(pattern_str, re.DOTALL)
        match_items = pattern.findall(source_str)

        update = {}
        for items in match_items:
            update.update({items: local_cache.get(items)})
        if len(match_items) > 0:  # 一次只能替换一个值，故几个待替换的值就需要几次替换
            source = Replace.replace_exec(pattern_str, source, update)
        return source

    @staticmethod
    def replace_keyword(source, pattern_str=r'\#.*?\#'):
        """
        替换数据中的关键字，替换为关键字对应方法执行的值
        :param source: 源数据
        :param pattern_str: 匹配规则
        :return: 替换后的数据
        """
        source_str = json.dumps(source)
        pattern = re.compile(pattern_str, re.DOTALL)
        match_items = list(set(pattern.findall(source_str)))
        update = {}
        for items in match_items:
            func_name = items.replace('#', '')
            func_object = getattr(KeyWords(), func_name)
            update.update({items: func_object()})
        if len(match_items) > 0:  # 一次只能替换一个值，故几个待替换的值就需要几次替换
            source = Replace.replace_exec(pattern_str, source, update)
        return source

    @staticmethod
    def replace_exec(pattern: str, source, update : dict):
        """
        根据pattern匹配的值，在update中查找对应的值，并替换到source中
        :param pattern: 匹配规则
        :param source: 源数据
        :param update: 替换的值
        :return: 替换后的数据
        """
        if isinstance(source, str):
            result = Replace.replace_str(pattern, source, update)
        elif isinstance(source, dict):
            result = Replace.replace_dict(pattern, source, update)
        else:
            result = source
        return result


    @staticmethod
    def replace_str(pattern: str, source: str, update: dict) -> str:
        """
        替换源数据为字符串时替换方法
        :param pattern: 匹配规则
        :param source: 源数据
        :param update: 替换的值
        :return: 替换后的数据认为字符串
        """
        re_pattern = re.compile(pattern, re.DOTALL)
        match_results = list(set(re_pattern.findall(source)))

        for item in match_results:
            source = source.replace(item, update.get(item))
        return source

    @staticmethod
    def replace_dict(pattern: str, source: dict, update) -> dict:
        """
        替换源数据为字典时替换方法
        :param pattern: 匹配规则
        :param source: 源数据
        :param update: 替换的值
        :return: 替换后的数据仍为字典
        """
        re_pattern = re.compile(pattern, re.DOTALL)
        match_results = re_pattern.findall(json.dumps(source))
        result = {}
        for match_item in match_results:
            result = replace(source, match_item, update.get(match_item))
        match_results = re_pattern.findall(json.dumps(result))
        if match_results:
            for match_item in match_results:
                result_str = json.dumps(result).replace(match_item, str(update.get(match_item)))
                result = json.loads(result_str)
        return result

def replace(source: dict, match_item: str, update) -> dict:
    """
    递归替换字典中各个层级的值
    :param source: 源数据
    :param match_item: 匹配的值
    :param update: 替换的值
    :return: 替换后的数据
    """
    for k, v in source.items():
        if isinstance(v, dict):
            source[k] = replace(v, match_item, update)
        elif isinstance(v, list):
            if match_item in v:
                match_index = v.index(match_item)
                v[match_index] = update
                source.update({k: v})
            else:
                for v_item in v:
                    if isinstance(v_item, dict):
                        source[k][v.index(v_item)] = replace(v_item, match_item, update)
        elif isinstance(v, str):
            if v == match_item:
                source.update({k: update})
            elif v.__contains__(match_item):
                replace_v = v.replace(match_item, str(update))
                source.update({k: replace_v})
            else:
                pass
        else:
            pass

    return source

def replace_key(source: dict, match_item: str, update)-> dict:
    """
    递归替换字典中各个层级的key
    :param source: 源数据
    :param match_item: 匹配的值
    :param update: 替换的值
    :return: 替换后的数据
    """
    for k, v in source.items():
        if isinstance(v, dict):
            source[k] = replace(v, match_item, update)
        else:
            pass
    return source


if __name__ == '__main__':
    update = {'$file_period_map$': 3320, '$set_date$': '2018-1-1'}
    source = {"json":{"task_id":"$financial_task_id$","table_type":"$financial_table_type$","template_id":"$template_id$","file_period_map":{"$file_period_map$":["$set_date$"]}}, "headers": { "Authorization": "Bearer $accessToken$" }}
    source = Replace.replace_exec(r'\$.*?\$', source, update)

