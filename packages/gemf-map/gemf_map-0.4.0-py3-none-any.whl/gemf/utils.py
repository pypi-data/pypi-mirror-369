"""
This submodule contains miscellaneous utilities for the `gemf` main module.
"""

import inspect
import json
import os
import re
from typing import Any, Dict, List, Type


# io
def listfiles(directory: str, formats: List[str] = []):
    """List all files in a directory. Optionally only list files of certain formats."""
    all_items = os.listdir(directory)
    files = [item for item in all_items if os.path.isfile(os.path.join(directory, item))]

    if formats:
        files = [file for file in files if any([file.endswith(format_) for format_ in formats])]

    return files

def listdirs(directory: str):
    """List all subdirectories in a directory."""
    all_items = os.listdir(directory)
    dirs = [item for item in all_items if os.path.isdir(os.path.join(directory, item))]
    return dirs


# check types
def is_jsonable(obj):
    """Whether an object can be serialized to json."""
    try:
        json.dumps(obj)
        return True
    except:
        return False

def to_json(obj):
    """If an object can be serialized to json, it will be returned unchanged. Else, a string representation of the object is returned."""
    if is_jsonable(obj):
        return obj
    else:
        return str(obj)


# formats
BYTE_STR_PNG = b'\x89PNG\r\n\x1a\n'; """Start byte sequence of a PNG file."""

BYTE_STR_JPG_START = b'\xff\xd8'; """Start byte sequence of a JPG file."""
BYTE_STR_JPG_END = b'\xff\xd9'; """End byte sequence of a JPG file."""

FORMAT_PATTERNS = {
    "empty": re.compile(b"^$"),
    "png": re.compile(re.escape(BYTE_STR_PNG)),
    "jpg": re.compile(BYTE_STR_JPG_START + b'.*?' + BYTE_STR_JPG_END, re.DOTALL)
}
"""Regex patterns to detect image formats in image byte data."""

def get_image_format(img_bytes, format_patterns: Dict[str, re.Pattern] = FORMAT_PATTERNS, raise_errors: bool = True):
    """Detect byte structure of image formats and return the corresponding format."""
    for format, format_pattern in format_patterns.items():
        if format_pattern.search(img_bytes):
            return format
    if raise_errors: raise ValueError(f"Could not identify image format in byte data. Supported formats: {list(format_patterns.keys())}")
    return None


# other
def kwargify(loc: dict, ignore: List[str] = []):
    """
    Automatically pass arguments as keyword arguments within `__init__` functions for `super()` calls.

    Particularly useful for multiple inheritance, supporting automatic dispatch of arguments to the
    respective superclasses (**assuming no duplicate parameter names**).

    # Usage
    ```python
    class C(A, B):
        def __init__(self, a, b):
            super().__init__(
                **kwargify(locals())
            )
    ```
    """
    # TODO: also inspect superclasses?
    ignore.append("self")

    curr_init = getattr(loc["__class__"], "__init__")
    params = inspect.signature(curr_init).parameters
    kwargs = {key: loc[key] for key in params if key not in ignore}
    return kwargs
