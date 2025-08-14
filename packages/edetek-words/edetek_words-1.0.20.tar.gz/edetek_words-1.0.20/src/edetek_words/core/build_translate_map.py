# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 8/8/2025 11:02 AM
@Description: Description
@File: build_translate_map.py
"""
import time

from edetek_words.common.json_utils import save_json
from edetek_words.common.path import docs_path
from edetek_words.common.translate_util import translate_multi_text
from edetek_words.core.build_map import load_data


def build_translate_map():
    main_lang_data = load_data("United States (English) SF-36v2 Acute Screen Shot Sample.json")
    main_lang = "en_US"
    oth_lang_data = load_data("Turkey (Turkish) SF-36v2 Acute Screen Shot Sample.json")
    oth_lang = "tr_TR"
    # translate_data = batch_translate(main_lang_data, main_lang, oth_lang)
    # save_json(str(docs_path("translate_test.json")), translate_data, ensure_ascii=False)
    translate_data = load_data("translate_test.json")
    print(set(oth_lang_data) & set(translate_data))


def batch_translate(texts, source_language, target_language, batch_size=20):
    """
    将 texts 按 batch_size 切分，多次调用 translate_multi_text
    :param texts: 要翻译的文本列表
    :param source_language: 源语言代码
    :param target_language: 目标语言代码
    :param batch_size: 每批请求的最大数量
    :return: 翻译结果列表（顺序与输入 texts 对应）
    """
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        # 调用你的翻译函数
        try:
            translated_batch = translate_multi_text(batch, source_language, target_language)
            translated_list = translated_batch.get("translatedList")
        except:
            print(batch)
            translated_list = []
        results.extend(translated_list)
        time.sleep(5)
    return results
