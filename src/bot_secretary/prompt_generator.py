import re

from jinja2 import Environment, PackageLoader, Template, select_autoescape
from pathlib import Path

from typing import Iterator


class Prompt:

    def __init__(self, template: Template, max_prompt_words: int, **kwargs):
        self.__template = template
        self.__re = re.compile(r"\b(?:\w+(?:\W+|$)){1,%d}" % (max_prompt_words - 1))
        self.__kwargs = kwargs

    def render(self) -> str:
        return self.__template.render(**self.__kwargs)

    @property
    def chunks(self) -> Iterator[str]:
        for chunk in self.__re.findall(str(self)):
            yield chunk


class PromptGenerator:

    def __init__(self, templates_folder: Path | None = None, max_prompt_words: int = 2500):
        self.__templates_folder = templates_folder or Path(__file__).parent / "templates"
        self.__max_prompt_words = max_prompt_words
        self.__env = self.__get_environment()

    def __get_environment(self) -> Environment:
        return Environment(
            loader=PackageLoader(
                package_name="prompt_templates",
                package_path=str(self.__templates_folder)
            ),
            autoescape=select_autoescape()
        )

    def __load_template(self, name: str) -> Template:
        path = self.__templates_folder / f"{name}.html"
        if not path.exists():
            raise FileExistsError(f"The template '{name}' doesn't exist in '{self.__templates_folder}'")
        return self.__env.get_template(f"{name}.html")

    @property
    def template_path(self) -> Path:
        return self.__templates_folder

    def dialog_settings(self) -> Prompt:
        return Prompt(self.__load_template("dialog_settings"), self.__max_prompt_words)

    def background_prompt(self, background_path: str | Path) -> Prompt:
        with open(background_path, 'r') as file:
            return Prompt(self.__load_template("background_prompt"), self.__max_prompt_words, text=file.read())

    def style_prompt(self, style_path: str | Path) -> Prompt:
        with open(style_path, 'r') as file:
            return Prompt(self.__load_template("style_prompt"), self.__max_prompt_words, text=file.read())

    def message_prompt(self, text: str) -> Prompt:
        return Prompt(self.__load_template("message_prompt"), self.__max_prompt_words, text=text)
