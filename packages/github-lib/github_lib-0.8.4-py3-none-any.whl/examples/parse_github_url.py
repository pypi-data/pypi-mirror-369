from gitlib.parsers.url import GithubUrlParser

parser = GithubUrlParser(url="https://github.com/janeczku/calibre-web/commit/7ad419dc8c12180e842a82118f4866ac3d074bc5")

print(parser())

parser = GithubUrlParser(url="https://github.com/janeczku/calibre-web")

print(parser())

parser = GithubUrlParser(url="https://github.com/0branch/boron/issues/3")

print(parser())

parser = GithubUrlParser(url="https://github.com/moby/moby/pull/35399/commits/a21ecdf3c8a343a7c94e4c4d01b178c87ca7aaa1")

print(parser())

parser = GithubUrlParser(url="https://github.com/vincentbernat/lldpd/releases")

print(parser())
