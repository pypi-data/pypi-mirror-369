# File Organizer CLI

A powerful and configurable command-line tool to organize your files effortlessly.

## Overview

This tool helps you keep your directories tidy by moving files into dedicated folders based on their extension, creation date, or custom rules you define.

## Features

*   Organize files by their extension (e.g., `.pdf`, `.jpg`, `.docx`).
*   Sort files into folders by creation date (e.g., `YYYY-MM-DD`).
*   Highly configurable using a `config.yaml` file.
*   Cross-platform and easy to use.

## Installation

You can install the File Organizer CLI directly from PyPI:

```bash
pip install kps-file-organizer
```

## Usage

Here are a couple of examples of how to use the tool.

### Organize by File Extension

This command will scan the specified directory and group files into subdirectories based on their extension (e.g., `pdf`, `jpg`, `txt`).

```bash
file-organizer /path/to/your/directory --by-extension
```

### Organize by Date

This command will scan the specified directory and group files into subdirectories based on their modification date.

```bash
file-organizer /path/to/your/directory --by-date
```

### Previewing Changes (Dry Run)

To see which files will be moved without actually performing the operation, use the `--dry-run` flag. This is highly recommended to run first.

```bash
file-organizer /path/to/your/directory --by-extension --dry-run
```

## Author

- **Krishna Pratap Singh**
- GitHub: [kps369](https://github.com/kps369)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
