from gitlib.models.url.repository import GithubRepoUrl


class GithubCommitUrl(GithubRepoUrl):
    sha: str
