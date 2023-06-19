import pytest

from jinja2 import Template
from pathlib import Path

from src.bot_secretary.prompt_generator import Prompt, PromptGenerator


def test_prompt_render(mock_template: Template):
    prompt = Prompt(mock_template, 2500, name='Test')
    assert prompt.render() == "Hello Test"


def test_prompt_chunks(mock_template: Template):
    prompt = Prompt(mock_template, 2500, name='Test')
    assert list(prompt.chunks) == ['Hello Test']


def test_prompt_chunks_lorem(mock_template_lorem: Template):
    prompt = Prompt(mock_template_lorem, 5)
    chunks = prompt.chunks
    assert len(chunks) == 14
    assert ''.join(chunks) == mock_template_lorem.render()


def test_prompt_generator_init(temp_dir):
    assert isinstance(PromptGenerator(temp_dir).template_path, Path)


def test_load_template_not_exist(temp_dir):
    with pytest.raises(FileExistsError):
        PromptGenerator(temp_dir).load_template('non_exist_template')
