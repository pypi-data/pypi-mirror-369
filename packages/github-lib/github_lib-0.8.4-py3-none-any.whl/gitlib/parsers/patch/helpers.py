import string

from typing import List, Tuple
from itertools import accumulate

from gitlib.common.enums import DiffLineType


MAP_DIFF_LINE_TYPE = {
    "-": DiffLineType.DELETION,
    "+": DiffLineType.ADDITION
}


def is_skippable_line(line: str) -> bool:
    """
    Check if the line should be skipped in the diff (Ignore comments or newline changes).

    :param line: The line to check.
    :return: True if the line should be skipped.
    """
    # TODO: maybe should cover more cases
    clean_line = line.strip()

    if not clean_line or clean_line.startswith("//") or clean_line.startswith("/*"):
        return True

    return False


def is_change_line(line: str) -> bool:
    """
    Check if the line is a change line in the diff.

    :param line: The line to check.
    :return: True if the line is a change line.
    """

    if len(line.strip()) == 0:
        return False

    return line[0] in ["-", "+"]


def parse_hunk_header(header: str) -> tuple[int, int]:
    """
    Parse a diff hunk header to extract line numbers.

    Args:
        header: The hunk header line (e.g., "@@ -1,7 +1,6 @@")

    Returns:
        tuple[int, int]: A tuple of (old_start, new_start) line numbers.
    """
    diff_info = [x.strip() for x in header.split("@@") if x.strip()]
    line_info = diff_info[0].split()

    old_start = int(line_info[0].split(",")[0].strip("-"))
    new_start = int(line_info[1].split(",")[0].strip("+"))

    return old_start, new_start


def shift_range(orig_one_line: str, formatted: str, included_chars: set):
    """
    Shifts the character ranges in a formatted string based on excluded characters.

    Args:
        orig_one_line (str): Original line from which the formatting was done.
        formatted (str): Formatted string.
        included_chars (set): Set of characters to include.

    Returns:
        list: List of shifted character ranges in the formatted string.
    """
    # Split the formatted string into lines and count included characters in each line
    formatted_lines = formatted.splitlines()
    formatted_char_count = [sum(1 for ch in line if ch in included_chars) for line in formatted_lines]

    # Calculate cumulative sum of included characters for each line
    formatted_range = list(accumulate(formatted_char_count))

    # Process original string and shift ranges
    for pos, ch in enumerate(orig_one_line):
        if ch not in included_chars:
            # Find indices where range >= pos
            for idx, val in enumerate(formatted_range):
                if val >= pos:
                    formatted_range[idx] += 1

    return formatted_range


def convert_column_pos_to_range(positions):
    ranges = []

    # Construct ranges between adjacent positions
    for i in range(1, len(positions)):
        start = positions[i - 1] + 1
        end = positions[i]
        ranges.append((start, end))

    # Add the initial range from 1 to the first position
    initial_range = (1, positions[0])
    ranges.insert(0, initial_range)

    return tuple(ranges)


def map_format_to_original_ranges(formatted_ranges: tuple, original_line_ranges: list):
    """
    Maps formatted ranges to corresponding original ranges in a text.

    Args:
        formatted_ranges (list of tuples): Ranges in the formatted text.
        original_line_ranges (list of ints): Line ranges in the original text.

    Returns:
        list of tuples: Original ranges corresponding to each formatted range.
    """
    mapping = []
    current_line = 1

    for i, format_range in enumerate(formatted_ranges):
        initial_line = current_line
        print(i+1, format_range, original_line_ranges[current_line])
        # Find the corresponding line in the original text for the start of the range
        if format_range[0] > original_line_ranges[current_line]:
            for current_line in range(current_line, len(original_line_ranges)):
                if format_range[0] <= original_line_ranges[current_line]:
                    break

        original_start_line = current_line
        original_start_column = format_range[0] - original_line_ranges[current_line - 1]

        # Find the corresponding line in the original text for the end of the range
        if format_range[1] > original_line_ranges[current_line]:
            for current_line in range(current_line, len(original_line_ranges)):
                if format_range[1] <= original_line_ranges[current_line]:
                    break

        original_end_line = current_line
        original_end_column = format_range[1] - original_line_ranges[current_line - 1]

        # Append the mapped range to the result
        mapping.append((original_start_line, original_start_column, original_end_line, original_end_column))
        print(initial_line == current_line)

    return mapping


# TODO: fix this function to make it work properly (unsure if shift or mapping is wrong)
def get_range_offset(orig: str, formatted: str) -> List[Tuple[int, int, int, int]]:
    """
    Matches the pretty-printed text with the original text, gets the corresponding row and
    column range in the original text for each line in the pretty-printed text.
    :param orig: The original text before pretty-printing.
    :param formatted: The pretty-printed text of the original text.
    :return: A list of 4-tuple of (row_start, col_start, row_end, col_end) in the original text
             for each line in the pretty-printed text.
    """
    orig_lines = orig.splitlines()
    orig_one_line = "".join(orig_lines)
    orig_line_widths = [len(x) for x in orig_lines]
    included_chars = set(string.printable) - set(string.whitespace)
    column_pos = shift_range(orig_one_line, formatted, included_chars)

    if column_pos:
        if column_pos[-1] != len(orig_one_line):
            raise ValueError('Size of formatted_range != size of orig_one_line')

        # Convert column_end pos to (column_start, column_end)
        column_range = convert_column_pos_to_range(column_pos)
        orig_line_range = [0] + list(accumulate(orig_line_widths))

        # Update orig pos for each line in the pretty-printed text
        return map_format_to_original_ranges(column_range, orig_line_range)

    return []


def get_pretty_printed(code: str, extension: str):
    """
            Performs pretty-printing on the whole files A and B
    """
    if extension in ['js', '.js', '.ts', '.tsx', '.jsx']:
        import jsbeautifier

        opts = jsbeautifier.default_options()
        opts.indent_size = 0

        return jsbeautifier.beautify(code, opts)
    else:
        # TODO: To be implemented for other programming languages
        print(f"Pretty-printing not implemented for {extension}.")
        return code
