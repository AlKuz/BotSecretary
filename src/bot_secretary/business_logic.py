from abc import ABC, abstractmethod
from loguru import logger
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler

from config import Config
from database.crud import CRUD, RoleMap, MessageTypeMap


class BaseExecutor(ABC):

    def __init__(self, config: Config):
        self._config = config
        self._crud = CRUD(config.database.uri)
        self._logger = logger.bind(classname=self.__class__.__name__)

    @abstractmethod
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raise NotImplementedError


class StartExecutor(BaseExecutor):

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not (await self._crud.is_user_exist(update.effective_user.id)):
            user_role = RoleMap.admin if (await self._crud.count_users()) == 0 else RoleMap.user
            await self._crud.create_user(update.effective_user.id, user_role)
            self._logger.info(f"New user '{update.effective_user.id}' connected to bot with role '{user_role.value}'")
        message = f"Hi, {update.effective_user.name}! I'm a {self._config.telegram.bot_name}. Let's have a chat!"
        await context.assistant.send_message(chat_id=update.effective_chat.id, text=message)


def add_handlers(app: Application, config: Config):
    app.add_handler(CommandHandler('start', StartExecutor(config)))
