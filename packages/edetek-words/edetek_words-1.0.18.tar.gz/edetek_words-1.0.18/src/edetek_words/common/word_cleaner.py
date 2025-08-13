# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/28/2025 5:07 PM
@Description: Description
@File: word_cleaner.py
"""
import re

_ZERO_WIDTH_PATTERN = re.compile(r'[\u200B\u200C\u200D\uFEFF]')
_CHECKBOX_PATTERN = re.compile(r'[\u2610\u2611\u2612]')


def clean_data(text: str) -> str:
    return clean_data_without_strip(text).strip()


def clean_data_without_strip(text: str) -> str:
    text = replace_nbsp(text)
    text = remove_zwsp(text)
    text = remove_checkbox(text)
    text = remove_extra_spaces(text)
    return text


def remove_zwsp(text: str) -> str:
    return _ZERO_WIDTH_PATTERN.sub('', text)


def replace_nbsp(text: str) -> str:
    return text.replace('\xa0', ' ')


def remove_checkbox(text: str) -> str:
    return _CHECKBOX_PATTERN.sub('', text)


def remove_extra_spaces(text: str) -> str:
    return re.sub(r' +', ' ', text)
