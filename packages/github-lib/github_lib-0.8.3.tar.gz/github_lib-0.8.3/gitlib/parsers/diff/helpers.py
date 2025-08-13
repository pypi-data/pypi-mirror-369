
def is_valid_patch(after_path_line: str) -> bool:
    """
    Check if the patch represents a valid file modification.
    :param after_path_line: The line containing the path of the file after modification.
    :return: True if the block is a valid modification.
    """

    # Only consider file modification, ignore file additions for now
    if not after_path_line.startswith("+++ "):
        print(f"Skipping block missing +++")
        return False

    # Ignore file deletions for now
    if after_path_line.endswith(" /dev/null"):
        return False  # Ignore deletions

    return True
