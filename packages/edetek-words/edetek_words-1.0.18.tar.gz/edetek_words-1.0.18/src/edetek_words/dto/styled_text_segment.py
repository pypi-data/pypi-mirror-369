# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/30/2025 11:09 AM
@Description: Description
@File: styled_text_segment.py
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


class FontStyle(Enum):
    BOLD = auto()
    ITALIC = auto()
    UNDERLINE = auto()


@dataclass
class StyledTextSegment:
    text: str
    styles: List[FontStyle] = field(default_factory=list)
