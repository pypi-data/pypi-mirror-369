# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/29/2025 10:12 AM
@Description: Description
@File: core.py
"""
from pathlib import Path
from typing import List, Dict

from loguru import logger

from edetek_words.common.docx_utils import accept_all_revisions
from edetek_words.common.logger import init_logger
from edetek_words.core.build_map import build_segment_map
from edetek_words.core.prepare import prepare_translation, prepare_translation_from_package
from edetek_words.core.word_extractor import WordExtractor
from edetek_words.core.word_replacer import WordReplacer
from edetek_words.dto.segment_dto import SegmentDTO
from edetek_words.dto.translation_package import TranslationPackage


def translate_word_from_package(payload: dict, strict_mode: bool = True, log_to_file: bool = False):
    init_logger(log_to_file=log_to_file)
    try:
        p: TranslationPackage = TranslationPackage.from_dict(payload)
        p.strict_mode = strict_mode
    except Exception as e:
        logger.error(f"Failed to parse TranslationPackage from payload: {e}")
        raise ValueError("Invalid translation package format") from e
    language = p.language
    src_path = Path(p.sourceDoc.path)
    dst_path = Path(p.sourceDoc.dstPath)
    filename = p.sourceDoc.name
    try:
        prepare_translation_from_package(src_path, dst_path)
        accept_all_revisions(dst_path)
        segments: List[SegmentDTO] = WordExtractor(str(dst_path)).extract()
        segment_map = build_segment_map(segments, language, filename, p)
        WordReplacer(str(dst_path)).replace(segment_map).save()
    except Exception as e:
        logger.error(f"Failed to translate Word document from package: {e}")
        raise RuntimeError(f"Translation failed for: {filename}") from e


def translate_word(work_dir, filename, target_language, target_language_name):
    dst_path = prepare_translation(work_dir, filename, target_language_name)
    accept_all_revisions(dst_path)
    segments: List[SegmentDTO] = WordExtractor(str(dst_path)).extract()
    segment_map = build_segment_map(segments, target_language, filename)
    WordReplacer(str(dst_path)).replace(segment_map).save()


def translate_words_multilang(work_dir: Path, filenames: List[str], target_languages: List[str],
                              lang_name_map: Dict[str, str]):
    for filename in filenames:
        src_path = work_dir / filename
        segments: List[SegmentDTO] = WordExtractor(str(src_path)).extract()
        for target_language in target_languages:
            target_language_name = lang_name_map.get(target_language, target_language)
            logger.info(f"Translating {filename} => {target_language_name}")
            dst_path = prepare_translation(work_dir, filename, target_language_name)
            segment_map = build_segment_map(segments, target_language, filename)
            WordReplacer(str(dst_path)).replace(segment_map).save()
            logger.info(f"✅ Finished translating '{filename}' => {target_language_name}")
