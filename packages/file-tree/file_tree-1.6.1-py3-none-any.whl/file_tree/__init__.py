"""FileTree representation of structured directory.

This top-level module contains:

    - :class:`file_tree.FileTree`:
        Main class representing a structured directory.
    - :func:`file_tree.convert`:
        Function to copy file from one FileTree to another.
    - :class:`template.Template`:
        Class representing an individual template within the FileTree.
    - `tree_directories`:
        Editable list of directories that will be searched for FileTrees.
    - :func:`parse_tree.extra_tree_dirs`:
        Context manager to temporarily add directories to `tree_directories`.
"""

import importlib.metadata

from .file_tree import FileTree, convert  # noqa: F401
from .parse_tree import extra_tree_dirs, tree_directories  # noqa: F401
from .template import Template  # noqa: F401

__version__ = importlib.metadata.version("file_tree")
