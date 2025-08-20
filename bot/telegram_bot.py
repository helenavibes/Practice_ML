import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from rabbitmq import send_to_rabbitmq

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context):
    update.message.reply_text('Отправьте данные для предсказания ML модели')

def handle_message(update: Update, context):
    user_id = update.effective_user.id
    message = {
        'user_id': user_id,
        'input_data': update.message.text
    }

    try:
        send_to_rabbitmq(message)
        update.message.reply_text('✅ Задача принята в обработку')
    except Exception as e:
        logger.error(f"Error sending to RabbitMQ: {e}")
        update.message.reply_text(f'❌ Ошибка: Не удалось отправить задачу')

def main():
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable is not set!")
        return

    updater = Updater(token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()