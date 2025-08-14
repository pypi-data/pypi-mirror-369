from pydantic import BaseModel
from typing import List, Iterator

from gitlib.models.diff.hunk import DiffHunk


# TODO: should have the sha of the file that was changed
class Patch(BaseModel):
    old_file: str
    new_file: str
    hunks: List[DiffHunk]

    def __iter__(self) -> Iterator[DiffHunk]:
        return iter(self.patches)

    def __str__(self):
        return "\n".join(str(hunk) for hunk in self.hunks)
