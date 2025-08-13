# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 8/22/2024 11:44 AM
@Description: Description
@File: run.py
"""
import ast

import datetime
import json
import os
from typing import Any


def sort_json_data(data: Any) -> Any:
    """
    Recursively sort JSON-like data (dictionaries and lists) and return the sorted data.

    :param data: JSON-like data (dict, list, or primitive).
    :return: Sorted JSON-like data.
    """

    def sort_key(item: Any) -> Any:
        if isinstance(item, dict):
            return tuple(sorted(item.items()))
        elif isinstance(item, list):
            return tuple(sort_key(subitem) for subitem in item)
        else:
            return item

    if isinstance(data, dict):
        # 对字典进行递归排序
        return {k: sort_json_data(v) for k, v in sorted(data.items())}
    elif isinstance(data, list):
        # 对列表进行排序，列表中的每一项也是递归排序的
        return sorted([sort_json_data(item) for item in data], key=sort_key)
    elif isinstance(data, str):
        try:
            parsed_data = ast.literal_eval(data)
            return sort_json_data(parsed_data)
        except (ValueError, SyntaxError):
            return data
    else:
        return data


def are_json_equal(str1, str2):
    """
    Compare two JSON strings by parsing, sorting, and then comparing the data.

    :param str1: First JSON string.
    :param str2: Second JSON string.
    :return: True if both JSON strings represent equivalent data, False otherwise.
    """
    try:
        data1 = json.loads(str1)
        data2 = json.loads(str2)
    except (json.JSONDecodeError, TypeError):
        raise ValueError("Invalid JSON string provided.")
    return sort_json_data(data1) == sort_json_data(data2)


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        if isinstance(obj, bytes):
            # return str(obj, encoding='utf-8')
            return bytes.decode(obj)
        return json.JSONEncoder.default(self, obj)


def save_json(file_path, data, sort_keys=True, indent=4, ensure_ascii=True):
    if not file_path or not isinstance(file_path, str):
        raise ValueError("文件路径不能为空，且必须为字符串。")
    if not file_path.lower().endswith('.json'):
        raise ValueError(f"文件路径无效：{file_path}，必须以 .json 结尾。")
    if not data:
        raise ValueError("待写入的对象不能为空。")
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=indent, sort_keys=sort_keys, cls=ComplexEncoder, ensure_ascii=ensure_ascii)
