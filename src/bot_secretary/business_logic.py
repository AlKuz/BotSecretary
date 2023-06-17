from abc import ABC, abstractmethod
from loguru import logger
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler

from config import Config


class BaseExecutor(ABC):

    def __init__(self, config: Config):
        self._config = config
        self._logger = logger.bind(classname=self.__class__.__name__)

    @abstractmethod
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raise NotImplementedError


class StartExecutor(BaseExecutor):

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = f"Hi, {update.effective_user.name}! I'm a {self._config.telegram.bot_name}. Let's have a chat!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        self._logger.info(f"User '{update.effective_user.id}' connected to bot")


def add_handlers(app: Application, config: Config):
    app.add_handler(CommandHandler('start', StartExecutor(config)))
