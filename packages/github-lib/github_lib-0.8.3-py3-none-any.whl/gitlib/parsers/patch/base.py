from abc import ABC
from typing import List

from gitlib.models.diff.patch import Patch
from gitlib.models.diff.hunk import DiffHunk
from gitlib.models.diff.line import DiffLine, DiffLineType

from gitlib.parsers.patch.helpers import is_change_line, is_skippable_line, MAP_DIFF_LINE_TYPE, parse_hunk_header


class PatchParser(ABC):
    def __init__(self, **kwargs):
        self.lines = None
        self.diff_hunk_parser = None
        self.file_name = None
        self.old_file_name = None

    def __call__(self) -> Patch:
        diff_hunks = []
        current_diff_hunk = None
        diff_hunk_lines = []
        hunk_ptr = 1

        for line in self.lines:
            if line.startswith("@@ "):
                if current_diff_hunk:
                    diff_hunk = current_diff_hunk(diff_hunk_lines)
                    diff_hunks.append(diff_hunk)

                current_diff_hunk = self.diff_hunk_parser(line, hunk_ptr)
                diff_hunk_lines = []
                hunk_ptr += 1

            if not current_diff_hunk:
                raise ValueError("Misaligned diff hunk")

            diff_hunk_lines.append(line)

        # Process the last diff hunk
        if diff_hunk_lines:
            diff_hunk = current_diff_hunk(diff_hunk_lines)
            diff_hunks.append(diff_hunk)

        return Patch(
            old_file=self.old_file_name,
            new_file=self.file_name,
            hunks=diff_hunks
        )


class DiffHunkParser:
    def __init__(self, header: str, order: int):
        self.old_start, self.new_start = parse_hunk_header(header)
        self.order = order

        # get the start line numbers from the diff hunk header.
        self.lineno_ptrs = {
            DiffLineType.DELETION: self.old_start,
            DiffLineType.ADDITION: self.new_start
        }

    def __call__(self, lines: List[str]) -> DiffHunk:
        """
            Parses the diff text chunks, gets the line numbers and the contents where diffs occur.
        """
        diff_lines = {
            DiffLineType.DELETION: [],
            DiffLineType.ADDITION: []
        }

        for i, line in enumerate(lines):
            if not is_change_line(line):
                for k, v in self.lineno_ptrs.items():
                    self.lineno_ptrs[k] += 1
                continue

            diff_line_type = MAP_DIFF_LINE_TYPE[line[0]]

            diff_lines[diff_line_type].append(
                DiffLine(
                    type=diff_line_type,
                    content=line[1:],
                    lineno=self.lineno_ptrs[diff_line_type] - 1,
                    skip=is_skippable_line(line[1:])
                )
            )

            # Increment the pointer for the specific diff line type
            self.lineno_ptrs[diff_line_type] += 1

        return DiffHunk(
            order=self.order,
            old_lines=diff_lines[DiffLineType.DELETION],
            new_lines=diff_lines[DiffLineType.ADDITION],
            old_start=self.old_start,
            new_start=self.new_start
        )
