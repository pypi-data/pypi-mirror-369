# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/30/2025 3:53 PM
@Description: Description
@File: run_.py
"""

from edetek_words.core.build_map import load_data
from edetek_words.core.core import translate_word_from_package

if __name__ == '__main__':
    payload: dict = load_data("payload.json")
    translate_word_from_package(payload, strict_mode=False)
