from typing import List
from pydantic import BaseModel

from gitlib.models.diff.line import DiffLine


class DiffHunk(BaseModel):
    order: int
    old_start: int
    new_start: int
    old_lines: List[DiffLine]
    new_lines: List[DiffLine]

    @property
    def old(self) -> str:
        return '\n'.join(line.content for line in self.old_lines)

    @property
    def new(self) -> str:
        return '\n'.join(line.content for line in self.new_lines)

    @property
    def ordered_lines(self) -> List[DiffLine]:
        """
        Returns all lines (old and new) in a single list sorted by line number.

        Returns:
            List[DiffLine]: A list of all lines sorted by their line numbers.
        """
        return sorted(self.old_lines + self.new_lines, key=lambda x: x.lineno)

    @property
    def deletions(self):
        return len(self.old_lines)

    @property
    def insertions(self):
        return len(self.new_lines)

    def __str__(self):
        header = f"{self.order} {self.__class__.__name__}({self.old_start}, {self.new_start})"

        for line in self.ordered_lines:
            if line.skip:
                continue
            # TODO: should account for padding size given the line number
            if line.type.value == '-':
                header += f"\n\t{line.lineno}     {line.type.value} {line.content}"
            else:
                header += f"\n\t    {line.lineno} {line.type.value} {line.content}"

        return header
