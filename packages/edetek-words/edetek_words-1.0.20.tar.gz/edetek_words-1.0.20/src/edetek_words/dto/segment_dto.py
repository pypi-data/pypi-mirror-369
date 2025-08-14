# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/30/2025 11:00 AM
@Description: Description
@File: rr_dto.py
"""
from dataclasses import dataclass, field
from typing import List, Optional

from edetek_words.dto.styled_text_segment import StyledTextSegment
from edetek_words.dto.translated_dto import TranslatedDTO


@dataclass
class SegmentDTO:
    original_text: str
    styled_segments: List[StyledTextSegment] = field(default_factory=list)
    translated_dto: Optional[TranslatedDTO] = field(default_factory=TranslatedDTO)
