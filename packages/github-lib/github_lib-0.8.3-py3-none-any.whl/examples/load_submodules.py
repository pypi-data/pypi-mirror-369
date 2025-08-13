from gitlib import GitClient

TOKEN = "YOUR_TOKEN_HERE"

client = GitClient(token=TOKEN)
repo = client.get_repo(owner="ONLYOFFICE", project="DocumentServer")
print(repo)

submodules = repo.get_submodules()

print(f"Found {len(submodules)} submodules in the repository.")

for submodule in submodules:
    print(f"Path: {submodule.path} | URL: {submodule.url} | Repo Path: {submodule.repo_path}")
