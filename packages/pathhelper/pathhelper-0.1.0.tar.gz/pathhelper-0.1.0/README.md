# PathHelper

**PathHelper** is a lightweight library for working with file and directory paths in Python. It provides simple interfaces and clear syntax for checking, creating, and removing paths — with helpful utilities for working in temporary directories.

---

## ✨ Features

- `FileHelper`: check, create, and remove files
- `DirHelper`: check, create, and remove directories
- `RunInDir`: context manager to temporarily change working directory
- Simplifies common scripting operations
- Minimal dependencies and clean API

---

## 📦 Installation

```bash
pip install pathhelper
```

---

## 🚀 Quick Example

```python
from pathhelper import DirHelper, FileHelper, RunInDir
import os

# Create a directory if it doesn't exist
dir_helper = DirHelper("temp_folder")
dir_helper.create_if_missing()

# Switch to that directory temporarily
with RunInDir("temp_folder"):
    print("Now inside:", os.getcwd())

# Clean up afterward
dir_helper.remove_if_present()

```

---

## 🔍 API Overview

| Class | Method / Constructor| Description|
|-------|---------------------|------------|
| FileHelper | `__init__(path)` | Initializes a file path helper with the given file path |
|          | `check_exists()` | Returns True if the file exists |
|          | `create()` | Creates the file and any necessary parent directories |
|          | `remove()` | Removes the file |
|          | `create_if_missing()` | Creates the file only if it doesn’t exist |
|          | `remove_if_present()` | Removes the file only if it exists |
| DirHelper  | `__init__(path)` | Initializes a directory path helper with the given directory path |
|          | `check_exists()` | Returns True if the directory exists |
|          | `create()` | Creates the directory (and parents) |
|          | `remove()` | Recursively removes the directory and contents |
|          | `create_if_missing()` | Creates the directory only if it doesn’t exist |
|          | `remove_if_present()` | Removes the directory only if it exists |
| RunInDir | `__init__(path)` | Initializes the context manager with a target path |
|          | `__enter__()` / `__exit__()` | Temporarily changes working directory within a with block |

## 🛠 Development Status

| Alpha — usable and tested, but subject to change

## 📄 License
MIT License

## 🔗 Links


* Package: [PyPi](https://pypi.org/project/pathhelper/)
* Developer docs: [Development Guide](doc/development_guide.md)
