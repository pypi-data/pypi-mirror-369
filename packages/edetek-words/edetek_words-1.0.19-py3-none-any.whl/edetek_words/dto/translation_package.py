# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/30/2025 3:22 PM
@Description: Description
@File: translation_package.py
"""

from dataclasses import dataclass, field
from typing import List, Optional

from loguru import logger

from edetek_words.common.word_cleaner import clean_data
from edetek_words.dto.base_dto import BaseDTO


@dataclass
class ContentItem(BaseDTO):
    text: str
    needAI: int
    translateText: str = None


@dataclass
class SourceDoc(BaseDTO):
    name: str
    path: str
    dstPath: str


@dataclass
class TranslationPackage(BaseDTO):
    language: str
    contents: List[ContentItem]
    sourceDoc: SourceDoc
    strict_mode: bool = field(default=True, metadata={"optional": True})

    def find_content_item_by_name(self, name: str) -> Optional[ContentItem]:
        if not self.contents:
            raise Exception("The contents list is empty or None.")
        for content in self.contents:
            if clean_data(content.text) == name:
                if content.text != name:
                    logger.info(f"ContentItem.text: '{content.text}' ||| name: '{name}'")
                return content
        if self.strict_mode:
            raise Exception(f"ContentItem with text '{name}' not found in contents.")
        return None
