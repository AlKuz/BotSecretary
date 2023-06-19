import openai

from abc import ABC, abstractmethod
from collections import defaultdict
from loguru import logger
from pathlib import Path
from telegram import Update
from telegram.ext import filters, Application, ContextTypes, CommandHandler, MessageHandler

from config import Config
from prompt_generator import PromptGenerator


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


class MessageExecutor(BaseExecutor):

    def __init__(self, config: Config):
        super().__init__(config)
        self.__prompt_generator = PromptGenerator(Path(__file__).parent / "prompt_templates")
        self.__messages: dict[int, list[dict]] = defaultdict(list)
        self.__system_context: list[dict] = [
            {"role": "system", "content": self.__prompt_generator.dialog_settings().render()},
            {"role": "system", "content": self.__prompt_generator.background_prompt(config.app.background_path).render()},
            {"role": "system", "content": self.__prompt_generator.style_prompt(config.app.style_path).render()},
        ]

    def __add_message(self, telegram_id: int, role: str, content: str):
        if len(self.__messages[telegram_id]) >= self._config.openai.max_messages:
            self.__messages[telegram_id].pop(0)
        self.__messages[telegram_id].append({"role": role, "content": content})

    def __get_prediction(self, telegram_id: int) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=self._config.openai.model,
                messages=self.__system_context + self.__messages[telegram_id],
                temperature=self._config.openai.temperature,
            )
            text = response["choices"][0]["message"]["content"]
        except openai.error.RateLimitError:
            text = "I'm sorry for the inconvenient, but I cannot answer on questions right now :("
        return text

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_id = update.effective_user.id
        self.__add_message(telegram_id, "user", content=update.message.text)
        text = self.__get_prediction(telegram_id)
        self.__add_message(telegram_id, "assistant", content=text)
        await update.message.reply_text(text)


def add_handlers(app: Application, config: Config):
    app.add_handler(CommandHandler('start', StartExecutor(config)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, MessageExecutor(config)))
