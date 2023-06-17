from telegram.ext import ApplicationBuilder

from business_logic import add_handlers
from config import Config


config = Config()
app = ApplicationBuilder().token(config.telegram.bot_token).build()
add_handlers(app, config)

app.run_polling()
