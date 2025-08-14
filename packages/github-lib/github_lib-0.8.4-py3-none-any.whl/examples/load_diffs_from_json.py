from gitlib.loader import DiffLoader

loader = DiffLoader("~/.gitlib")

diff_dict = loader.load()

for diff in diff_dict:
    print(diff)
