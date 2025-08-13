# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/28/2025 4:55 PM
@Description: Description
@File: path.py
"""
import sys
from pathlib import Path


def root() -> Path:
    return up_path(Path(__file__), 4)


def project_root() -> Path:
    return up_path(Path(__file__), 2)


def docs_path(*args) -> Path:
    return project_root() / "docs" / Path(*args)


def up_path(path: Path, levels: int = 1) -> Path:
    for _ in range(levels):
        path = path.parent
    return path.resolve()


def output_path(*args: str) -> Path:
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = project_root()
    return base_path.joinpath(*args)


def output_doc_path(*args: str) -> Path:
    output_doc_dir = output_path("docs")
    output_doc_dir.mkdir(parents=True, exist_ok=True)
    return output_doc_dir.joinpath(*args)
