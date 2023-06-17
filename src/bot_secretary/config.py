from pathlib import Path
from pydantic import BaseSettings, BaseModel


class OpenAI(BaseModel):
    api_token: str


class Telegram(BaseModel):
    bot_name: str
    bot_token: str


class Config(BaseSettings):

    openai: OpenAI
    telegram: Telegram

    class Config:
        env_nested_delimiter = '__'
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = 'utf-8'
