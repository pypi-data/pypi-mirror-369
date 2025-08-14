import configparser

from typing import List, Optional
from pydantic import BaseModel


class Submodule(BaseModel):
    """
    Represents a submodule in a Git repository.
    """
    path: str
    url: str
    repo_path: Optional[str] = None


class Submodules(BaseModel):
    """
    Represents a collection of submodules in a Git repository.
    """
    elements: List[Submodule]

    def __len__(self):
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)

    def get_submodule_by_path(self, path: str) -> Optional[Submodule]:
        return next((s for s in self.elements if s.path == path), None)

    def get_submodule_by_name(self, name: str) -> Optional[Submodule]:
        return next((s for s in self.elements if s.name == name), None)

    @classmethod
    def parse_gitmodules(cls, owner: str, content: str) -> 'Submodules':
        """Parse .gitmodules content into validated Submodules object."""
        config = configparser.ConfigParser()
        config.read_string(content)

        _submodules = []

        for section in config.sections():
            _submodule = Submodule(
                path=config[section]['path'], url=config[section]['url'],
            )

            url_parts = _submodule.url.split('/')

            if len(url_parts) > 1 and url_parts[0] == '..':
                # Extract the repository name from the URL
                repo_name = url_parts[-1].replace('.git', '')
                _submodule.repo_path = f"{owner}/{repo_name}"

            _submodules.append(_submodule)

        return cls(elements=_submodules)
