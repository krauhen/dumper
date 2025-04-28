"""Configuration for ignore patterns in the dumper tool.

This module defines pattern lists for various development environments
and tools, indicating which files and directories should be ignored
during the dumping process.
"""

from typing import List


PYTHON_IGNORE_PATTERNS: List[str] = [
    ".venv",
    "venv",
    "__pycache__",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".eggs",
    "build",
    "dist",
    ".coverage",
    ".python-version",
    "poetry.lock",
    "_.egg-info",
]

NODE_IGNORE_PATTERNS: List[str] = [
    "node_modules",
    ".next",
    ".nuxt",
    ".angular",
    "bower_components",
    "jspm_packages",
    "coverage",
    ".cache",
    "build",
    "dist",
    ".eslintcache",
    "yarn-error.log",
    "yarn.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    ".DS_Store",
]

GIT_IGNORE_PATTERNS: List[str] = [
    ".git",
    ".gitmodules",
    ".gitattributes",
    ".gitkeep",
    ".git-rewrite",
]

INTELLIJ_IGNORE_PATTERNS: List[str] = [".idea"]

GENERAL_IGNORE_PATTERNS: List[str] = [
    ".pdf",
    ".doxc",
    ".xlsx",
    ".pem",
    ".pyc",
]
