# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/28/2025 4:57 PM
@Description: Description
@File: build_map.py
"""
import copy
from pathlib import Path
from typing import Dict, List

from edetek_words.common.constant import EN_US, TranslationRequirement
from edetek_words.common.json_utils import save_json
from edetek_words.common.path import docs_path, output_doc_path
from edetek_words.common.read_file import connect_to
from edetek_words.common.translate_util import translate_multi_text, extraction_semantic
from edetek_words.dto.segment_dto import SegmentDTO
from edetek_words.dto.styled_text_segment import StyledTextSegment
from edetek_words.dto.translation_package import TranslationPackage, ContentItem


def build_segment_map(segments: List[SegmentDTO], target_language, filename, package: TranslationPackage = None
                      ) -> Dict[str, SegmentDTO]:
    """
    Translate a list of segments and build a mapping from original text to translated SegmentDTO.

    :param segments: List of SegmentDTO objects containing original text and optional style segments.
    :param target_language: Target language code (e.g. "ja_JP") for translation.
    :param filename: The source filename, used to name the debug JSON output.
    :param package: Optional package, reserved for future use.
    :return: A dictionary mapping original text to the translated SegmentDTO.
    :raises Exception: If the number of translated texts does not match the number of original texts.
    """
    original_texts = [segment.original_text for segment in segments]
    payload = translate_multi_text(original_texts, EN_US, target_language)
    translate_text_path = output_doc_path(f"{Path(filename).stem}_translate_text_{target_language}.json")
    if translate_text_path.exists() and translate_text_path.is_file():
        translate_text_path.unlink()
    save_json(str(translate_text_path), payload, ensure_ascii=False)  # for debug
    translated_list = payload["translatedList"]
    translate_map = dict()
    if len(original_texts) == len(translated_list):
        debug_data = list()
        for idx in range(len(original_texts)):
            original_segment = segments[idx]
            segment = copy.deepcopy(original_segment)
            translated_text = translated_list[idx]
            if package and package.contents:
                content: ContentItem = package.find_content_item_by_name(segment.original_text)
                if content:
                    if content.needAI == TranslationRequirement.REQUIRED_NO_AI.value:
                        translated_text = content.translateText
                    elif content.needAI == TranslationRequirement.NOT_REQUIRED.value:
                        continue
            segment.translated_dto.translated_text = translated_text
            translate_map.update({segment.original_text: segment})
            styled_segments = segment.styled_segments
            if not styled_segments:
                continue
            if len(styled_segments) == 1 and segment.original_text == styled_segments[0].text:
                trans_styled_segments = [StyledTextSegment(translated_text, styled_segments[0].styles)]
                segment.translated_dto.styled_segments = trans_styled_segments
            else:
                styled_segments_text = [styled_segment.text for styled_segment in styled_segments]
                extracted_texts = extraction_semantic(styled_segments_text, translated_text, EN_US, target_language)
                if extracted_texts:
                    if len(styled_segments_text) == len(extracted_texts):
                        trans_styled_segments = []
                        for styled_idx in range(len(styled_segments_text)):
                            trans_styled_segment = StyledTextSegment(extracted_texts[styled_idx])
                            trans_styled_segment.styles = styled_segments[styled_idx].styles
                            trans_styled_segments.append(trans_styled_segment)
                        segment.translated_dto.styled_segments = trans_styled_segments
                        debug_data.append({
                            "source_text_list": styled_segments_text,
                            "original_text": segment.original_text,
                            "target_text": translated_text,
                            "extracted_texts": extracted_texts,
                            "equal": translated_text in extracted_texts
                        })
        if debug_data:
            extraction_semantic_path = output_doc_path(f"{Path(filename).stem}_extraction_semantic_{target_language}.json")
            if extraction_semantic_path.exists() and extraction_semantic_path.is_file():
                extraction_semantic_path.unlink()
            save_json(str(extraction_semantic_path), debug_data, ensure_ascii=False)  # for debug
    else:
        raise Exception(
            f"Translation count mismatch: {len(original_texts)} original texts vs {len(translated_list)} translated texts. "
        )
    return translate_map


def load_data(filename):
    text_filepath = docs_path(filename)
    connector = connect_to(str(text_filepath), ignore_error=True)
    return connector and connector.data or []
