from typing import List, Optional
from github.Repository import Repository
from github import GithubException, RateLimitExceededException

from gitlib.models.diff import Diff
from gitlib.models.submodule import Submodules

from gitlib.github.commit import GitCommit
from gitlib.common.exceptions import GitLibException
from gitlib.parsers.patch.unified import UnifiedPatchParser


class GitRepo:
    """
        Represents a GitHub repository.
    """

    def __init__(self, repo: Repository):
        self.repo = repo

    @property
    def id(self):
        return self.repo.id

    @property
    def owner(self):
        return self.repo.owner

    @property
    def commits_count(self) -> int:
        return self.repo.get_commits().totalCount

    @property
    def language(self) -> str:
        return self.repo.language

    @property
    def description(self) -> str:
        return self.repo.description

    @property
    def size(self) -> int:
        return self.repo.size

    @property
    def stars(self) -> int:
        return self.repo.stargazers_count

    @property
    def forks(self) -> int:
        return self.repo.forks_count

    @property
    def watchers(self) -> int:
        return self.repo.watchers_count

    @property
    def name(self) -> str:
        return self.repo.name

    def get_commit(self, sha: str, raise_err: bool = False) -> GitCommit | None:
        # Ignore unavailable commits
        try:
            # self.app.log.info(f"Getting commit {commit_sha}")
            return GitCommit(self.repo.get_commit(sha=sha), repo_id=self.id)
        except (ValueError, GithubException):
            err_msg = f"Commit {sha} for repo {self.repo.name} unavailable."
        except RateLimitExceededException as rle:
            err_msg = f"Rate limit exhausted: {rle}"

        if raise_err:
            raise GitLibException(err_msg)

        # TODO: implement some logging

        return None

    def get_diff(self, base: str, head: str) -> Diff:
        """
            Get the diff between two commits.

            :param base: The base commit sha.
            :param head: The head commit sha.

            :return: A Diff object.
        """

        # make sure the commits are available
        base_commit = self.get_commit(base)
        head_commit = self.get_commit(head)

        # make sure the base commit precedes the head commit
        if base_commit.date > head_commit.date:
            raise GitLibException(f"Base commit {base} does not precede head commit {head}")

        patches = []

        for file in head_commit.files:
            base_file = self.repo.get_contents(file.filename, ref=base_commit.sha)
            base_content = base_file.decoded_content.decode("utf-8")

            parser = UnifiedPatchParser(a_str=base_content, b_str=file.content,
                                        old_file=base_file.path, new_file=file.filename)
            patch = parser()

            patches.append(patch)

        return Diff(
            repo_id=self.id,
            commit_sha=head_commit.sha,
            patches=patches
        )

    def get_versions(self, limit: int = None) -> List[str]:
        releases = self.repo.get_releases()

        if releases.totalCount > 0:
            if limit and releases.totalCount > limit:
                # Return the latest n releases
                return [release.tag_name for release in releases[:limit]]
            else:
                return [release.tag_name for release in releases]
        else:
            tags = self.repo.get_tags()

            if limit and tags.totalCount > limit:
                return [tag.name for tag in tags[:limit]]
            else:
                return [tag.name for tag in tags]

    def get_submodules(self) -> Optional[Submodules]:
        """
            Get the list of submodules in the repository.

            :return: A list of submodule names.
        """

        try:
            gitmodules_file = self.repo.get_contents('.gitmodules')

            if gitmodules_file:
                content = gitmodules_file.decoded_content.decode('utf-8')
                submodules = Submodules.parse_gitmodules(self.owner.name, content)

                return submodules

        except GithubException as e:
            print(f"Error getting submodules: {e}")

        return None
