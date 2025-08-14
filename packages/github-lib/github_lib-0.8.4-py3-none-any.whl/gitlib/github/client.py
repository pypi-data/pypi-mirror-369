
from github import Github
from github import RateLimitExceededException, UnknownObjectException, GithubException

from gitlib.github.repository import GitRepo
from gitlib.common.exceptions import GitLibException


class GitClient:
    """
        Client for interacting with the GitHub API.

        Note: This library is currently focused on GitHub-specific functionality
        and does not interact with other Git services like GitLab or plain Git.
    """

    def __init__(self, token: str, **kwargs):
        if not token:
            # TODO: consider using the token from the environment
            # if not environ.get('GITHUB_TOKEN', None):
            raise GitLibException("No GitHub token provided")

        self.git_api = Github(token, **kwargs)

    @property
    def remaining(self) -> int:
        return self.git_api.get_rate_limit().core.remaining

    def get_repo(self, owner: str, project: str, raise_err: bool = False) -> GitRepo | None:
        repo_path = '{}/{}'.format(owner, project)

        try:
            print(f"Getting repo {repo_path}")
            return GitRepo(self.git_api.get_repo(repo_path))
        except RateLimitExceededException as rle:
            err_msg = f"Rate limit exhausted: {rle}"
        except UnknownObjectException:
            err_msg = f"Repo not found. Skipping {owner}/{project} ..."
        except GithubException as ge:
            err_msg = f"Error getting repo: {ge}"

        if raise_err:
            raise GitLibException(err_msg)

        # TODO: implement some logging

        return None
