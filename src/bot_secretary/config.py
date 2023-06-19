from pathlib import Path
from pydantic import BaseSettings, BaseModel


class OpenAI(BaseModel):
    api_token: str
    model: str
    max_messages: int
    temperature: float


class Telegram(BaseModel):
    bot_name: str
    bot_token: str


class Application(BaseModel):
    background_path: str
    style_path: str


class Config(BaseSettings):

    openai: OpenAI
    telegram: Telegram
    app: Application

    class Config:
        env_nested_delimiter = '__'
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = 'utf-8'
