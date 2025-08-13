from pathlib import Path
from typing import Iterator, List


from gitlib.models.diff.patch import Patch
from gitlib.common.constants import DEFAULT_FILENAMES_TO_SKIP


class DiffParser:
    def __init__(self, extensions: list = None, skip_filenames: tuple = DEFAULT_FILENAMES_TO_SKIP, **kwargs):
        self.patches = None

        self.extensions = extensions if extensions else []
        self.skip_filenames = skip_filenames if skip_filenames else []

    def __iter__(self) -> Iterator[Patch]:
        return iter(self.patches)

    def __call__(self) -> List[Patch]:
        pass

    def _is_valid_extension(self, file_path: str) -> bool:
        """
        Check if the line's file extension matches the desired extensions.
        :param file_path: The file path from the diff line.
        :return: True if the extension is valid or extensions are not filtered.
        """
        if not self.extensions:
            return True

        return Path(file_path).suffix in self.extensions

    def _should_skip_filename(self, old_file: str, new_file: str) -> bool:
        """
        Check if a patch should be skipped based on its file paths.

        :param old_file: The old file path.
        :param new_file: The new file path.

        :return: True if the block should be skipped.
        """
        if not self.skip_filenames:
            return False

        for filename in self.skip_filenames:
            if filename in old_file or filename in new_file:
                return True

        return False
