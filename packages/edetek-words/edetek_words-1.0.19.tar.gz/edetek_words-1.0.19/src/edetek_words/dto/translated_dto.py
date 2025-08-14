# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/29/2025 2:18 PM
@Description: Description
@File: translated_dto.py
"""
from dataclasses import dataclass, field
from typing import List

from edetek_words.dto.styled_text_segment import StyledTextSegment


@dataclass
class TranslatedDTO:
    translated_text: str = ""
    styled_segments: List[StyledTextSegment] = field(default_factory=list)
