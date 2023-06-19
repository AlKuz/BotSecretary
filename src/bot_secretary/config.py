from pathlib import Path
from pydantic import BaseSettings, BaseModel
from urllib.parse import quote


class OpenAI(BaseModel):
    api_token: str


class Telegram(BaseModel):
    bot_name: str
    bot_token: str


class Database(BaseModel):
    host: str | None
    port: int | None
    engine: str
    username: str | None
    password: str | None
    db_name: str

    @property
    def uri(self) -> str:
        username = quote(self.username) if self.username else ''
        password = quote(self.password) if self.password else ''
        host = self.host if self.host else ''
        port = f":{self.port}" if self.port else ''
        return f"{self.engine}+asyncpg://{username}:{password}@{host}{port}/{self.db_name}"


class Config(BaseSettings):

    openai: OpenAI
    telegram: Telegram
    database: Database

    class Config:
        env_nested_delimiter = '__'
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = 'utf-8'
