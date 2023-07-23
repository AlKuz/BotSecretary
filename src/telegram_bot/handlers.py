from abc import ABC, abstractmethod
from loguru import logger
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import filters, Application, ContextTypes, CommandHandler, MessageHandler

from .backend_client import Client
from .config import Config
from .schemas import Context, UUID4, MessageRequest, MessageResponse


class BaseExecutor(ABC):

    def __init__(self, config: Config):
        self._config = config
        self._client = Client(config.telegram.backend_url)
        self._logger = logger.bind(classname=self.__class__.__name__)

    @abstractmethod
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raise NotImplementedError


class StartExecutor(BaseExecutor):

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = f"Hi again, {update.effective_user.name} :)"
        if not context.user_data.get("lex_context"):
            user_id: UUID4 | None = await self._client.get_user_id(update.effective_user.id)
            if not user_id:
                user_id: UUID4 | None = await self._client.create_user(update.effective_user.id)
                if user_id:
                    self._logger.info(f"New user '{update.effective_user.id}' was created")
                    context.user_data["lex_context"] = Context(user_id=user_id)
                    message = f"Hi, {update.effective_user.name}! Let's have a chat!"
                else:
                    message = "Sorry, something goes wrong :("
        await context.assistant.send_message(chat_id=update.effective_chat.id, text=message)


class MessageExecutor(BaseExecutor):

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.user_data.get("lex_context"):
            user_id = await self._client.get_user_id(update.effective_user.id)
            context.user_data["lex_context"] = Context(user_id=user_id)
        lex_context: Context = context.user_data["lex_context"]
        request = MessageRequest(
            input_text=update.message.text,
            bot_name=self._config.lex.bot_name,
            bot_alias=self._config.lex.bot_alias,
            **lex_context.dict()
        )
        response: MessageResponse = await self._client.send_message(request)
        context.user_data["lex_context"] = Context(user_id=lex_context.user_id, **response.dict())
        await update.message.reply_text(response.message)
        for attachment in response.attachments:
            message = attachment.title
            keyboard = [InlineKeyboardButton(b.text, callback_data=b.value) for b in attachment.buttons]
            reply_markup = InlineKeyboardMarkup([keyboard])
            await update.message.reply_text(message, reply_markup=reply_markup)


def add_handlers(app: Application, config: Config):
    app.add_handler(CommandHandler('start', StartExecutor(config)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, MessageExecutor(config)))
