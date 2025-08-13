from functools import cached_property
from pathlib import Path
from typing import Optional
import tomllib
import re


class PythonProject:
    def __init__(self, path: Path):
        self.path = path
        self.toml = tomllib.loads(path.read_text())

    @cached_property
    def name(self) -> str:
        return self.find_value((
            ('project', 'name'),
            ('tool', 'poetry', 'name'),
        ))

    """
    Get the normalized name of the distribution, according to the Python Packaging Authority (PyPa) guidelines.
    This is used to create the name of the zip file.
    The name is normalized by replacing any non-alphanumeric characters with underscores.
    https://peps.python.org/pep-0427/#escaping-and-unicode
    """
    @cached_property
    def distribution_name(self) -> str:
        return re.sub("[^\w\d.]+", "_", self.name, re.UNICODE)

    @cached_property
    def entrypoint_package_name(self) -> str:
        """
        The subdirectory name in the source virtual environment's site-packages that contains the function's entrypoint
        code.
        """
        # TODO : Parse out the project's package dir(s) if defined.  Use the first one if there are multiple.
        return self.distribution_name

    def find_value(self, paths: tuple[tuple[str]]) -> str:
        for path in paths:
            value = self.get_value(path)
            if value is not None:
                return value
        raise Exception("TODO Exception find_value")

    def get_value(self, path: tuple[str]) -> Optional[str]:
        node = self.toml
        for name in path:
            node = node.get(name)
            if node is None:
                return None
        return node
