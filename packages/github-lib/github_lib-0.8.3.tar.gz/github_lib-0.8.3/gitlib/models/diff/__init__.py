from pydantic import BaseModel
from typing import List, Iterator


from gitlib.models.diff.patch import Patch


class Diff(BaseModel):
    repo_id: int
    commit_sha: str
    patches: List[Patch]

    def __iter__(self) -> Iterator[Patch]:
        return iter(self.patches)

    def __str__(self):
        return "\n".join(str(_patch) for _patch in self.patches)
