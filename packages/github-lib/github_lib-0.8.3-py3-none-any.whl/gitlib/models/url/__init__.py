from gitlib.common.enums import GithubUrlType
from gitlib.models.url.base import GithubUrl
from gitlib.models.url.repository import GithubRepoUrl
from gitlib.models.url.commit import GithubCommitUrl
from gitlib.models.url.issue import GithubIssueUrl
from gitlib.models.url.pull_request import GithubPullRequestUrl, GithubPRCommitUrl


GITHUB_MODELS = {
    GithubUrlType.REPOSITORY: GithubRepoUrl,
    GithubUrlType.COMMIT: GithubCommitUrl,
    GithubUrlType.ISSUE: GithubIssueUrl,
    GithubUrlType.PULL_REQUEST: GithubPullRequestUrl,
    GithubUrlType.PR_COMMIT: GithubPRCommitUrl,
}
