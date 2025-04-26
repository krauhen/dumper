"""Core functionality for the dumper tool.

This module contains functions for walking directories, dumping file
structures and contents, and optionally using AI for summarization of file
contents.
"""

import asyncio
import openai
import os

from itertools import chain
from pathlib import Path
from typing import List, Optional, Iterable
from dumper.config import (
    PYTHON_IGNORE_PATTERNS,
    NODE_IGNORE_PATTERNS,
    GIT_IGNORE_PATTERNS,
    INTELLIJ_IGNORE_PATTERNS,
)


DEFAULT_IGNORE_PATTERNS: List[str] = [
    *PYTHON_IGNORE_PATTERNS,
    *NODE_IGNORE_PATTERNS,
    *GIT_IGNORE_PATTERNS,
    *INTELLIJ_IGNORE_PATTERNS,
]


def is_ignored(path: Path, ignore_patterns: List[str]) -> bool:
    """Check if the given path should be ignored based on patterns.

    Args:
        path (Path): The filesystem path to check.
        ignore_patterns (List[str]): Patterns used to determine if the path is ignored.

    Returns:
        bool: True if the path matches any ignore pattern, False otherwise.
    """
    match = any(part in ignore_patterns for part in path.parts)
    return match


def walk_files(
    root: Path, recursive: bool = False, ignore_patterns: Optional[List[str]] = None
) -> Iterable[Path]:
    """Walk through files in a directory tree.

    Args:
        root (Path): The root directory to walk.
        recursive (bool): Recursively walk subdirectories if True.
        ignore_patterns (List[str], optional): Patterns determining files to ignore.

    Yields:
        Iterable[Path]: An iterable of file paths.
    """
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS
    if recursive:
        for path in root.rglob("*"):
            if path.is_file() and not is_ignored(path, ignore_patterns):
                yield path
    else:
        for path in root.iterdir():
            if path.is_file() and not is_ignored(path, ignore_patterns):
                yield path


def dump_tree(
    root: Path, depth: int = 1, ignore_patterns: Optional[List[str]] = None
) -> str:
    """Generate a directory tree representation as a string.

    Args:
        root (Path): The root directory to show.
        depth (int): The depth to which the directory tree is shown.
        ignore_patterns (List[str], optional): Patterns for ignoring files/directories.

    Returns:
        str: The formatted directory tree.
    """
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS
    root = root.resolve()
    lines = []
    max_depth = len(root.parts) + depth

    def _walk(path: Path):
        if len(path.parts) > max_depth:
            return
        if is_ignored(path, ignore_patterns):
            return
        if path != root:
            rel = path.relative_to(root)
            lines.append(f"./{rel}" + ("/" if path.is_dir() else ""))
        if path.is_dir():
            for child in sorted(path.iterdir(), key=lambda x: x.name):
                _walk(child)

    _walk(root)
    return "\n".join(lines)


async def sum_up_lines_async(lines, paths, model_name, openai_api_key):
    """Summarize lines asynchronously using an AI model.

    Args:
        lines (list): Lines of file content to summarize.
        paths (list): Corresponding file paths.
        model_name (str): The AI model name to use for summarization.
        openai_api_key (str): The API key for OpenAI service.

    Returns:
        list: Summarized file contents.
    """
    os.environ["OPENAI_API_KEY"] = openai_api_key

    async def fetch_summary(prompt, path, client, model_name):
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert text summarizer. "
                    "Summarize the given file content into a short text summary. "
                    "Use technical terms that are industry standard. "
                    "Format the response with: "
                    f"// Summary of file {path}:\n",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=128,
            top_p=1,
        )
        return response.choices[0].message.content.strip()

    prompts = [f"Sum up the following:\n{line}" for line in lines]

    async with openai.AsyncOpenAI() as client:
        tasks = [
            fetch_summary(prompt, path, client, model_name)
            for path, prompt in zip(paths, prompts)
        ]
        return await asyncio.gather(*tasks)


def dump_files(
    root: Path,
    recursive: bool = False,
    ignore_patterns: Optional[List[str]] = None,
    keep_patterns: Optional[List[str]] = None,
    sum_up: bool = False,
    model_name: Optional[str] = None,
    openai_api_key: Optional[str] = None,
) -> str:
    """Dump files in a root directory, optionally summarizing them.

    Args:
        root (Path): The root directory containing files to dump.
        recursive (bool): Recursively include subdirectories if True.
        ignore_patterns (List[str], optional): Patterns used to ignore files.
        keep_patterns (List[str], optional): Patterns to remove from the ignore list.
        sum_up (bool): Summarize file content using AI if True.
        model_name (str, optional): AI model name for summarization.
        openai_api_key (str, optional): OpenAI API key for AI access.

    Returns:
        str: The dumped file content.
    """
    if ignore_patterns is not None:
        ignore_patterns = list(
            dict.fromkeys([*ignore_patterns, *DEFAULT_IGNORE_PATTERNS])
        )
    else:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS

    if keep_patterns is not None:
        [
            ignore_patterns.remove(pattern)
            for pattern in keep_patterns
            if pattern in ignore_patterns
        ]

    lines = []
    paths = []

    for path in walk_files(root, recursive, ignore_patterns):
        file_lines = []
        file_lines.append(f"// File content of {path}:")
        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                file_lines.extend([line.rstrip("\n") for line in f])
        except Exception as e:
            file_lines.append(f"// ERROR reading {path}: {e}")
        file_lines.append("")
        lines.append(file_lines)
        paths.append(path)

    if sum_up:
        results = asyncio.run(
            sum_up_lines_async(lines, paths, model_name, openai_api_key)
        )
        lines = [
            "\n".join(line) + "\n" + result + "\n"
            for line, result in zip(lines, results)
        ]
    else:
        lines = list(chain.from_iterable(lines))

    return "\n".join(lines)
