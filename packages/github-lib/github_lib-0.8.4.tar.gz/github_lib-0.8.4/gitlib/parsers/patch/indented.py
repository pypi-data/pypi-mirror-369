import difflib
import warnings

from gitlib.parsers.patch.base import PatchParser
from gitlib.parsers.patch.helpers import get_range_offset, get_pretty_printed


class IndentedPatchParser(PatchParser):
    """
        Parser for returning indented patches.
        Useful for diffs that are not properly formatted (e.g., js minimized code).
        Warning: This parser is experimental and may not work as expected.
    """
    def __init__(self, a_str: str, b_str: str, extension: str = None, **kwargs):
        warnings.warn("IndentedPatchParser is experimental and may not work as expected", UserWarning, stacklevel=2)
        super().__init__(**kwargs)
        self.a_formatted = get_pretty_printed(a_str, extension)
        self.a_formatted_range = get_range_offset(a_str, self.a_formatted)

        self.b_formatted = get_pretty_printed(b_str, extension)
        self.b_formatted_range = get_range_offset(b_str, self.b_formatted)

        self.lines = list(
            difflib.unified_diff(
                a=self.a_formatted.splitlines(keepends=True),
                b=self.b_formatted.splitlines(keepends=True)
            )
        )

    def __call__(self, *args, **kwargs):
        patch = super().__call__()

        for hunk in patch.hunks:
            for line in hunk.lines:
                formatted_range = self.b_formatted_range if line.type.value == '+' else self.a_formatted_range
                idx = line.lineno - 1
                line.lineno = formatted_range[idx][0]

                ## TODO: DiffLine to be extended with the following fields
                # line.scol = formatted_range[idx][1]
                # line.eline = formatted_range[idx][2]
                # line.ecol = formatted_range[idx][3]
