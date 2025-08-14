# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/28/2025 5:09 PM
@Description: Description
@File: run_translate_word.py
"""
from pathlib import Path

from edetek_words.core.core import translate_word

if __name__ == '__main__':
    work_dir = Path(r"D:\melen\docs\Temp-own\20250728_translate\workdir")
    # filename = "CRN04894-13_GC Dosing Diary_v3.0_Final Draft.docx"
    filename = "CRN04894-13_Menstrual Cycle Diary_V1.0_final draft.docx"
    target_language = "ja_JP"
    target_language_name = "Japanese (Japan)"
    # target_language = "fr_FR"
    # target_language_name = "French (France)"
    translate_word(work_dir, filename, target_language, target_language_name)
