import json

from pathlib import Path
from typing import Dict, Iterator
from dataclasses import dataclass, field

from gitlib.models.diff import Diff


@dataclass
class DiffDictionary:
    entries: Dict[str, Diff] = field(default_factory=dict)

    def add_entry(self, diff: Diff):
        self.entries[diff.commit_sha] = diff

    def __iter__(self) -> Iterator[Diff]:
        return iter(self.entries.values())

    def __len__(self):
        return len(self.entries)


class DiffLoader:
    def __init__(self, path: str):
        self.path = Path(path).expanduser()

        if not self.path.exists():
            raise FileNotFoundError(f"Path '{path}' does not exist.")

    def __call__(self) -> Iterator[Diff]:
        """
            Lazily load diffs from the specified path.
        """

        for diff_path in self.path.iterdir():
            with diff_path.open("r") as diff_file:
                diff_json = json.load(diff_file)
                diff = Diff.parse_obj(diff_json)

                yield diff

    def load(self) -> DiffDictionary:
        """
            Eagerly loads diffs from the specified path.
        """

        diff_dict = DiffDictionary()

        for diff in self():
            diff_dict.add_entry(diff)

        return diff_dict
