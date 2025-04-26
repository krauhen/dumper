# dumper

**dumper** is a command-line tool for dumping the structure and contents of directories, with optional file summarization using OpenAI models. It efficiently lists project directory trees, reads files (with customizable ignore patterns), and can generate AI-powered summaries of file contents.

---

## Features

- **Project Tree Output**: Display a tree view of your directory up to a specified depth.
- **File Content Dump**: Output the content of all (non-ignored) files in the directory.
- **Custom Ignore Patterns**: Exclude files/folders by default or via extra patterns (Python, Node.js, Git, IDE caches, etc.).
- **AI Summarization**: (Optional) Use OpenAI models to generate concise summaries for each file's content.
- **Command-Line Simplicity**: Powered by [Click](https://click.palletsprojects.com/).

---

## Installation

### For usage in local active venv

```bash
$ source venv/bin/activate
$ pip install .
```

### For usage system-wide

```bash
$ deactivate
$ pip install . --break-system-packages
$ dumper --help
```

## For development

```bash
$ poetry env use 3.12.9
$ eval $(poetry env activate)
$ poetry install
$ dumper --help
```

---

## Usage

To dump a project directory, run:

```bash
dumper --root /path/to/project
```

### Options

- `--root PATH` _(required)_: Directory to dump.
- `--tree-depth N`: Show directory tree up to depth _N_ (default: 1).
- `--recursive/--no-recursive`: Recurse subdirectories when dumping files (default: False).
- `--add-ignore-list PAT1,PAT2,...`: Comma-separated substrings to skip (appended to the default ignore list).
- `--remove-ignore-list PAT1,PAT2,...`: Comma-separated substrings to remove from ignore list.
- `--only-tree`: Only print the directory tree and exit.
- `--sum-up-files`: Summarize file content with OpenAI.
- `--model-name NAME`: OpenAI model name to use for summarization (default: `gpt-4o-mini`).
- `--openai-api-key KEY`: OpenAI API key (can also be provided via environment variable).

### Example Usage

- **Show directory tree up to depth 2 and dump file contents:**

  ```bash
  $ dumper --root . --tree-depth 2 --recursive
  ```

- **Add ignore patterns and only print the tree:**

  ```bash
  $ dumper --root ./project --add-ignore-list ".history,.vscode" --only-tree
  ```

- **Dump content and summarize files with OpenAI:**

  ```bash
  $ dumper --root ./src --recursive --sum-up-files --openai-api-key sk-...
  ```
  
- **Dump content and summarize files with OpenAI into a file output.txt (ignore this otherwise this results in a infinit loop):**

  ```bash
  $ OPENAI_API_KEY=sk-... dumper --root . --recursive --tree-depth 3 --sum-up-files --add-ignore-list "output.txt" > output.txt
  ```

---

## Default Ignore Patterns

By default, dumper ignores common files and folders found in many Python, Node.js, git, and IDE-managed projects. These include:

- **Python**: `.venv`, `venv`, `__pycache__`, `.ruff_cache`, `.tox`, `.eggs`, `build`, `dist`, etc.
- **Node**: `node_modules`, `.next`, `.nuxt`, `.angular`, `bower_components`, `dist`, etc.
- **Git**: `.git`, `.gitattributes`, `.gitmodules`, etc.
- **IDE/OS files**: `.idea`, `.DS_Store`, etc.

You can add more by passing comma-separated patterns to `--add-ignore-list`.

---

## License

MIT

---

## Author

Henning Krause (<henning.krause90@gmail.com>)