from typing import List, Tuple

from gitlib.models.diff.patch import Patch
from gitlib.parsers.diff.base import DiffParser
from gitlib.parsers.patch.git import GitPatchParser
from gitlib.parsers.diff.helpers import is_valid_patch


class GitDiffParser(DiffParser):
    def __init__(self, diff_text: str, **kwargs):
        """
            Initializes the CommitDiff object with the given commit.
            :param extensions: A list of file extensions to filter the diff by.
            :param skip_filenames: A tuple of filenames to skip in the diff. Default is ('test',).
        """
        super().__init__(**kwargs)
        self.diff_text = diff_text

    def __call__(self) -> List[Patch]:
        patches = []

        # TODO: find a better way to split the diff text into patches
        for patch_str in filter(lambda x: x != '', self.diff_text.split("diff --git ")):
            result = self._process_patch(patch_str)

            if result is None:
                continue

            processed_patch, old_path, new_path = result
            patch_parser = GitPatchParser(processed_patch, new_path, old_path)
            patch = patch_parser()
            patches.append(patch)

        return patches

    def _process_patch(self, patch: str) -> Tuple[List[str], str, str] | None:
        # Ensure the block has at least two lines, also, we are considering only modifications
        patch_lines = patch.splitlines()

        if len(patch_lines) < 4:
            return None

        before_path_line = patch_lines[2]
        after_path_line = patch_lines[3]

        # Ensure the block is not a deletion and has a valid "+++" line
        if not is_valid_patch(after_path_line):
            return None

        # Skip blocks not matching the extensions
        if not self._is_valid_extension(after_path_line):
            return None

        # Create the DiffBlock object
        # Format of the "---" and "+++" lines:
        # --- a/<a_path>
        # +++ b/<b_path>
        old_path = before_path_line[len("--- a/"):]
        new_path = after_path_line[len("+++ b/"):]

        # Skip blocks containing filenames to be ignored
        if self._should_skip_filename(old_path, new_path):
            return None

        return patch_lines[4:], old_path, new_path
