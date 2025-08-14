from enum import Enum


class DiffLineType(Enum):
    """
        Enum for different types of diff line prefixes.
    """
    ADDITION = "+"
    DELETION = "-"


class GithubUrlType(Enum):
    REPOSITORY = "repository"
    COMMIT = "commit"
    ISSUE = "issue"
    PULL_REQUEST = "pull_request"
    PR_COMMIT = "pr_commit"

    # TODO: add more types if necessary
