from gitlib.models.url.repository import GithubRepoUrl


class GithubPullRequestUrl(GithubRepoUrl):
    number: str


class GithubPRCommitUrl(GithubPullRequestUrl):
    sha: str
