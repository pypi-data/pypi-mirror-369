# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/30/2025 11:32 AM
@Description: Description
@File: prepare.py
"""
import os.path
import shutil
from pathlib import Path

from loguru import logger


def prepare_translation(work_dir: Path, filename: str, language_name: str):
    src_path = work_dir / filename
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source file does not exist: {src_path}")
    dst_dir = work_dir / language_name
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst_path = dst_dir / filename
    if dst_path.exists() and dst_path.is_file():
        dst_path.unlink()
    shutil.copy(src_path, dst_path)
    logger.info(f"The file ({os.path.basename(dst_path)}) has been copied successfully.")
    return dst_path


def prepare_translation_from_package(src_path: Path, dst_path: Path):
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source file does not exist: {src_path}")
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    if dst_path.exists() and dst_path.is_file():
        dst_path.unlink()
    shutil.copy(src_path, dst_path)
    logger.info(f"The file ({os.path.basename(dst_path)}) has been copied successfully.")
