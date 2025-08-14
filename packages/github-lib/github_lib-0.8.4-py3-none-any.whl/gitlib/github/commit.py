import requests

from typing import List
from github.Commit import Commit

from gitlib.models.diff import Diff
from gitlib.github.file import GitFile
from gitlib.parsers.diff.git import GitDiffParser


class GitCommit:
    def __init__(self, commit: Commit, repo_id: int):
        self.repo_id = repo_id
        self.commit = commit
        self._files = None
        self._diff = None

    @property
    def parents(self):
        return [GitCommit(parent, self.repo_id) for parent in self.commit.parents]

    @property
    def html_url(self):
        return self.commit.html_url

    @property
    def message(self):
        return self.commit.commit.message

    @property
    def sha(self):
        return self.commit.sha

    @property
    def date(self):
        return self.commit.commit.author.date

    @property
    def stats(self):
        return self.commit.stats

    @property
    def state(self):
        return self.commit.get_combined_status().state

    @property
    def files(self) -> List[GitFile]:
        if self._files is None:
            self._files = [GitFile(file) for file in self.commit.files]

        return self._files

    def get_file(self, file: GitFile) -> GitFile:
        """
            Get the file from the commit.

            :param file: The subsequent file to get in the current version.
        """
        # look for the file in the list of files
        for f in self.files:
            if f.filename == file.filename:
                return f

    @property
    def diff(self) -> str:
        # Lazy load the diff
        if not self._diff:
            self._diff = requests.get(f"{self.commit.html_url}.diff").text

        return self._diff

    def get_diff(self) -> Diff:
        """
            By default, the diff is obtained by using the diff URL.
        """

        parser = GitDiffParser(self.diff)
        patches = parser()

        # TODO: temporary solution to represent and keep track of the diff
        return Diff(
            repo_id=self.repo_id,
            commit_sha=self.commit.sha,
            patches=patches
        )
