# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/30/2025 10:02 AM
@Description: Description
@File: constant.py
"""
EN_US = "en_US"

from enum import Enum


class TranslationRequirement(Enum):
    NOT_REQUIRED = -1  # 不需要翻译
    REQUIRED_NO_AI = 0  # 需要翻译，但不需要 AI
    REQUIRED_WITH_AI = 1  # 需要翻译，需要 AI
