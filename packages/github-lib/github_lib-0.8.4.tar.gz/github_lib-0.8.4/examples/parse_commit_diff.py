import json

from pathlib import Path
from gitlib import GitClient

TOKEN = "YOUR_GITHUB_TOKEN"

client = GitClient(token=TOKEN)
repo = client.get_repo(owner="ArtifexSoftware", project="mujs")
print(repo)

commit = repo.get_commit(sha="fa3d30fd18c348bb4b1f3858fb860f4fcd4b2045")
print(commit)

commit_diff = commit.get_diff()

print("# COMMIT DIFF #")
print(commit_diff)

print("# SAVING COMMIT DIFF TO JSON #")
commit_json = commit_diff.model_dump(mode="json")

output_path = Path(f"~/.gitlib/{commit_diff.commit_sha}.json").expanduser()

with output_path.open(mode="w") as f:
    json.dump(commit_json, f, indent=2)

print("# REPO UNIFIED DIFF #")
repo_diff = repo.get_diff(commit.parents[0].sha, commit.sha)
print(repo_diff)
