from gitlib.models.url.repository import GithubRepoUrl


class GithubIssueUrl(GithubRepoUrl):
    number: str
