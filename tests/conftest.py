import pytest
import tempfile
import shutil

from jinja2 import Template
from pathlib import Path
from typing import Iterator


@pytest.fixture
def mock_template() -> Template:
    return Template("Hello {{ name }}")


@pytest.fixture
def mock_template_lorem() -> Template:
    return Template("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
                    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris "
                    "nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
                    "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non "
                    "proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")


@pytest.fixture
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)
