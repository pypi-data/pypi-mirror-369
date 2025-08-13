from gitlib.common.enums import GithubUrlType


DEFAULT_FILENAMES_TO_SKIP = ('test', )

OWNER_GROUP = r"(?P<owner>[^/]+)"
REPO_GROUP = r"(?P<repo>[^/]+)"
REPO_PATH = f"/{OWNER_GROUP}/{REPO_GROUP}"

# Resource patterns
SHA_GROUP = r"(?P<sha>[0-9a-f]{5,40})"
NUMBER_GROUP = r"(?P<number>\d+)"

# TODO: complement regex expression to extract information from the following github references
# e.g., https://github.com/intelliants/subrion/commits/develop
# # e.g., https://github.com/{owner}/{repo}/commits/master?after={sha}+{no_commits}
# e.g., https://github.com/{owner}/{repo}/commits/{branch}
GITHUB_URL_PATTERNS = {
    GithubUrlType.REPOSITORY: f"{REPO_PATH}/?$",
    GithubUrlType.COMMIT: f"{REPO_PATH}/commit/{SHA_GROUP}",
    GithubUrlType.ISSUE: f"{REPO_PATH}/issues/{NUMBER_GROUP}",
    GithubUrlType.PR_COMMIT: f"{REPO_PATH}/pull/{NUMBER_GROUP}/commits/{SHA_GROUP}",
    GithubUrlType.PULL_REQUEST: f"{REPO_PATH}/pull/{NUMBER_GROUP}"
}
