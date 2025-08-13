# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/29/2025 11:36 AM
@Description: Description
@File: docx_utils.py
"""
import os
from typing import List

import pythoncom
import win32com.client as win32
from loguru import logger

from edetek_words.common.word_cleaner import clean_data


def accept_all_revisions(docx_path):
    try:
        pythoncom.CoInitialize()
        logger.info("Launching Word Application...")
        word = win32.Dispatch("Word.Application")
    except Exception as e:
        logger.exception("Failed to launch Word via COM. Is Office installed and registered?")
        raise
    word.Visible = False
    doc = word.Documents.Open(os.path.abspath(docx_path))
    try:
        rev_count = doc.Revisions.Count
        comments_count = doc.Comments.Count
        if rev_count == 0 and comments_count == 0:
            logger.info("No revisions or comments; skipping.")
            return
        doc.TrackRevisions = False
        doc.AcceptAllRevisions()
        for comment in doc.Comments:
            comment.Delete()
        doc.Save()
    except Exception as e:
        logger.exception("Failed during Word document processing.")
        raise
    finally:
        doc.Close(False)
        word.Quit()
        pythoncom.CoUninitialize()


def get_bold_semantic_texts(para):
    result = []
    bold_chunk = ""
    for run in para.runs:
        if run.bold or run.text.strip() == "":
            bold_chunk += run.text
        else:
            if bold_chunk.strip():
                result.append(clean_data(bold_chunk))
                bold_chunk = ""
    if bold_chunk.strip():
        result.append(clean_data(bold_chunk))
    return result


def parse_text_segments(translated_text: str, bold_texts: List[str]) -> List[tuple]:
    if not bold_texts:
        return [(translated_text, False)]
    text_segments = []
    remaining_text = translated_text
    for bold_text in bold_texts:
        if bold_text in remaining_text:
            start_pos = remaining_text.find(bold_text)
            if start_pos > 0:
                text_segments.append((remaining_text[:start_pos], False))
            text_segments.append((bold_text, True))
            remaining_text = remaining_text[start_pos + len(bold_text):]
    if remaining_text:
        text_segments.append((remaining_text, False))
    return text_segments


def apply_text_segments_to_runs(runs, first_valid_run_idx: int, text_segments: List[tuple]):
    first_run = runs[first_valid_run_idx]
    for i, (text, is_bold) in enumerate(text_segments):
        if text:
            if i == 0:
                first_run.text = text
                first_run.bold = is_bold
            else:
                if first_valid_run_idx + i < len(runs):
                    current_run = runs[first_valid_run_idx + i]
                    current_run.text = text
                    current_run.bold = is_bold
                else:
                    new_run = first_run._element.getparent().add_run(text)
                    new_run.bold = is_bold
