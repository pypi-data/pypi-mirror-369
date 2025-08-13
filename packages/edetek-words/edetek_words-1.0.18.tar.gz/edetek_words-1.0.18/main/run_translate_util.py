# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/28/2025 6:31 PM
@Description: Description
@File: run_translate_util.py
"""
from edetek_words.common.translate_util import translate_multi_text

if __name__ == '__main__':
    translated_texts = translate_multi_text(["HELLO", "world", "hoe are you?"], "en_US", "zh_CN")
    print(translated_texts)
