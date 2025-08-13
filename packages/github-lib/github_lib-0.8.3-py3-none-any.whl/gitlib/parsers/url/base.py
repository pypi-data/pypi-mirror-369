import re

from pydantic import HttpUrl, ValidationError

from gitlib.models.url import GithubUrl, GITHUB_MODELS
from gitlib.common.constants import GITHUB_URL_PATTERNS


# TODO: extend to parse other hosts
# e.g., https://gitlab.gnome.org/GNOME/gthumb/commits/master/extensions/cairo_io/cairo-image-surface-jpeg.c
class GithubUrlParser:
    def __init__(self, url: str):
        try:
            self.url = HttpUrl(url)
        except ValidationError:
            self.url = None

    def is_valid(self) -> bool:
        return self.url is not None

    def is_github_url(self) -> bool:
        return self.is_valid() and self.url.host == "github.com"

    def __call__(self) -> GithubUrl | None:
        if self.is_github_url():
            # Clean up the URL when it ends with /releases
            if self.url.path.endswith("/releases"):
                self.url = HttpUrl(str(self.url).replace("/releases", ""))

            for model_class, pattern in GITHUB_URL_PATTERNS.items():
                match = re.match(pattern, self.url.path)

                if match:
                    return GITHUB_MODELS[model_class](url=self.url, **match.groupdict())

        return None
