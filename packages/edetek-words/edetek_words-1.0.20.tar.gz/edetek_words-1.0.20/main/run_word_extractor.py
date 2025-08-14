# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/28/2025 2:11 PM
@Description: Description
@File: run_extractor.py
"""
from pathlib import Path

from edetek_words.common.docx_utils import accept_all_revisions
from edetek_words.core.prepare import prepare_translation
from edetek_words.core.word_extractor import WordExtractor

if __name__ == '__main__':
    work_dir = Path(r"C:\Users\LiXiaodong\Downloads\SF-36v2 翻译文本")
    filename = "Turkey (Turkish) SF-36v2 Acute Screen Shot Sample.docx"
    # filename = "CRN04894-13_Menstrual Cycle Diary_V1.0_final draft.docx"
    target_language_name = "Turkish"
    dst_path = prepare_translation(work_dir, filename, target_language_name)
    accept_all_revisions(dst_path)
    WordExtractor(dst_path).extract()
