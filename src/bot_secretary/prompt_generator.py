import re

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from pathlib import Path


class Prompt:

    def __init__(self, template: Template, max_prompt_words: int, **kwargs):
        self.__template = template
        self.__re = re.compile(r"\b(?:\w+(?:\W+|$)){1,%d}" % max_prompt_words)
        self.__kwargs = kwargs

    def render(self) -> str:
        return self.__template.render(**self.__kwargs)

    @property
    def chunks(self) -> list[str]:
        return self.__re.findall(self.render())


class PromptGenerator:

    def __init__(self, templates_folder: Path | None = None, max_prompt_words: int = 2500):
        self.__templates_folder = templates_folder or Path(__file__).parent / "prompt_templates"
        self.__max_prompt_words = max_prompt_words
        self.__env = self.__get_environment()

    def __get_environment(self) -> Environment:
        return Environment(
            loader=FileSystemLoader(str(self.__templates_folder)),
            autoescape=select_autoescape()
        )

    def load_template(self, name: str) -> Template:
        path = self.__templates_folder / f"{name}.html"
        if not path.exists():
            raise FileExistsError(f"The template '{name}' doesn't exist in '{self.__templates_folder}'")
        return self.__env.get_template(f"{name}.html")

    @property
    def template_path(self) -> Path:
        return self.__templates_folder

    def dialog_settings(self) -> Prompt:
        return Prompt(self.load_template("dialog_settings"), self.__max_prompt_words)

    def background_prompt(self, background_path: str | Path) -> Prompt:
        with open(background_path, 'r') as file:
            return Prompt(self.load_template("background_prompt"), self.__max_prompt_words, text=file.read())

    def style_prompt(self, style_path: str | Path) -> Prompt:
        with open(style_path, 'r') as file:
            return Prompt(self.load_template("style_prompt"), self.__max_prompt_words, text=file.read())

    def message_prompt(self, text: str) -> Prompt:
        return Prompt(self.load_template("message_prompt"), self.__max_prompt_words, text=text)
