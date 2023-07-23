from pathlib import Path
from pydantic import BaseSettings, BaseModel


class Telegram(BaseModel):
    bot_name: str
    bot_token: str
    backend_url: str


class Lex(BaseModel):
    bot_name: str
    bot_alias: str


class Config(BaseSettings):

    telegram: Telegram
    lex: Lex

    class Config:
        env_nested_delimiter = '__'
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = 'utf-8'
