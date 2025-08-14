from gitlib.models.url.base import GithubUrl


class GithubRepoUrl(GithubUrl):
    owner: str
    repo: str

    def __str__(self):
        return f"{self.owner}/{self.repo}"
