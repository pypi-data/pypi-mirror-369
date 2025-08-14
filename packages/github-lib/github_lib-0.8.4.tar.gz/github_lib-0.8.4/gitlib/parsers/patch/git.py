from pathlib import Path

from gitlib.parsers.patch.base import PatchParser
from gitlib.parsers.patch.unified import DiffHunkParser


class GitPatchParser(PatchParser):
    def __init__(self, patch: str | list, file_name: str, old_file_name: str, **kwargs):
        super().__init__(**kwargs)
        self.old_file_name = old_file_name
        self.file_name = file_name
        self.extension = Path(file_name).suffix
        self.lines = patch.splitlines() if isinstance(patch, str) else patch
        self.diff_hunk_parser = DiffHunkParser
