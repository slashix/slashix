import logging
import openai
from telegram.ext import Updater, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BOT_TOKEN = 'TELEGRAM_BOT_TOKEN'
OPENAI_API_KEY = 'OPENAI_API_TOKEN'
ALLOWED_NICKNAMES = ['nickname_1', 'nickname_2']

def chat(update, context):
    if update.message.from_user.username not in ALLOWED_NICKNAMES:
        update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    message = update.message.text
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt='User: ' + message,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    ).get("choices")[0].text
    update.message.reply_text(response)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    updater = Updater(BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("chat", chat))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
