import difflib

from gitlib.parsers.patch.base import PatchParser, DiffHunkParser


class UnifiedPatchParser(PatchParser):
    """ Parser to process the changes and their location in code from patches

        Attributes:
            :param a_str: The contents of file A.
            :param b_str: The contents of file B.
    """
    def __init__(self, a_str: str, b_str: str, old_file: str, new_file: str, **kwargs):
        super().__init__(**kwargs)
        self.old_file_name = old_file
        self.file_name = new_file
        self.lines = list(difflib.unified_diff(
            a=a_str.splitlines(),
            b=b_str.splitlines(),
            lineterm='')
        )
        # TODO: temporary solution, might not work properly for all cases
        self.lines = [line.rstrip('\n') for line in self.lines[2:]]
        self.diff_hunk_parser = DiffHunkParser
