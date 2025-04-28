"""Command-line interface definition for the dumper tool.

This module provides the CLI for the dumper application, allowing users
to dump directory structures and optionally summarize file contents using AI.
"""

import click
import os
import sys

from pathlib import Path

from pydantic import SecretStr

from .core import dump_tree, dump_files, DEFAULT_IGNORE_PATTERNS
from .settings import get_settings


settings = get_settings()
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], max_content_width=180)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--root",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory to dump, e.g., --root /path/to/dir",
)
@click.option(
    "--recursive/--no-recursive",
    default=False,
    help="Recurse subdirectories? Use --recursive to enable.",
)
@click.option(
    "--tree-depth",
    default=1,
    show_default=True,
    type=int,
    help="Depth to print tree. E.g., --tree-depth 3 for a deeper view.",
)
@click.option(
    "--add-ignore-list",
    multiple=True,
    default=list(),
    help="Extra substrings to skip, multiple allowed. E.g., --add-ignore-list '.git', '.env'",
)
@click.option(
    "--remove-ignore-list",
    multiple=True,
    default=list(),
    help="Substrings to remove from skipping list, multiple allowed. E.g., --remove-ignore-list 'build', 'dist'",
)
@click.option(
    "--only-tree",
    is_flag=True,
    help="Only print project tree and exit.",
)
@click.option(
    "--sum-up-files",
    is_flag=True,
    help="Sum up file content with AI. Use --sum-up-files to enable summarization.",
)
@click.option(
    "--model-name",
    type=click.Choice(["gpt-4o", "gpt-4o-mini"], case_sensitive=False),
    default="gpt-4o-mini",
    show_default=True,
    help="Model name used for summarization. Choices are 'gpt-4o', 'gpt-4o-mini'.",
)
@click.option(
    "--openai-api-key",
    hide_input=True,
    default=None,
    show_default=True,
    help="OpenAI API key. Prompt is hidden for security.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity of the output. Use '-v', '-vv', etc. to increase the level.",
)
def main(
    root,
    recursive,
    tree_depth,
    add_ignore_list,
    remove_ignore_list,
    only_tree,
    sum_up_files,
    model_name,
    openai_api_key,
    verbose,
):
    """Dumps directory structure and file contents with optional AI summarization.

    Args:\n
        root (Path): The root directory to dump.\n
        recursive (bool): Whether to recurse subdirectories.\n
        tree_depth (int): The depth to print the directory tree.\n
        add_ignore_list (list of str): Extra patterns to ignore.\n
        remove_ignore_list (list of str): Patterns to remove from the ignore list.\n
        only_tree (bool): If true, only print the directory tree and exit.\n
        sum_up_files (bool): If true, summarize file contents using AI.\n
        model_name (str): The name of the model for summarization.\n
        openai_api_key (str): API key for OpenAI services.\n
        verbose (int): The verbosity level of output.\n
    """
    if not sum_up_files:
        ...
    elif openai_api_key and sum_up_files:
        print(f"Provided OpenAI API key is: {SecretStr(openai_api_key)}")
    elif settings.openai_api_key and sum_up_files:
        openai_api_key = settings.openai_api_key
        print(f"Settings OpenAI API key is: {SecretStr(openai_api_key)}")
    elif os.environ.get("OPENAI_API_KEY", None) and sum_up_files:
        openai_api_key = os.environ["OPENAI_API_KEY"]
        print(f"Environment OpenAI API key is: {SecretStr(openai_api_key)}.")
    else:
        raise Exception(
            "If you want to sum up file contents, you need to specify an OpenAI API key."
        )

    ignore_patterns = list(DEFAULT_IGNORE_PATTERNS)
    ignore_patterns.extend(add_ignore_list)
    keep_patterns = list(remove_ignore_list)

    if verbose > 0:
        click.echo(f"Verbosity level: {verbose}")

    click.echo(f"Directory structure (depth {tree_depth}) under '{root}':")

    tree_output = dump_tree(root, tree_depth, ignore_patterns)
    click.echo(tree_output)
    click.echo()

    if only_tree:
        sys.exit(0)

    file_output = dump_files(
        root,
        recursive,
        ignore_patterns,
        keep_patterns,
        sum_up_files,
        model_name,
        openai_api_key,
    )
    click.echo(file_output)


if __name__ == "__main__":
    main()
