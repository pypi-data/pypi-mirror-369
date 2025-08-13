from typing import List

from gitlib.models.diff.patch import Patch
from gitlib.parsers.diff.base import DiffParser


class UnifiedDiffParser(DiffParser):
    # TODO: Implement the unified diff parser, for now it is just a placeholder
    def __init__(self, patches: List[Patch], **kwargs):
        super().__init__(**kwargs)
        self.patches = patches

    def __call__(self) -> List[Patch]:
        return self.patches
