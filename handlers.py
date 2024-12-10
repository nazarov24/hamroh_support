from telegram import Update
from telegram.ext import ContextTypes
from settings import (
    TELEGRAM_SUPPORT_CHAT_ID,
    FORWARD_MODE,
    PERSONAL_ACCOUNT_CHAT_ID,
    WELCOME_MESSAGE,
)
import logging


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение при выполнении команды /start."""
    await update.message.reply_text(
    f"Здравствуйте, {update.effective_user.first_name}! 👋 "
    "\nДобро пожаловать в бот поддержки Hamroh. "
    "\nЗдесь вы можете задать вопросы, оставить отзывы или сообщить о проблемах.")




async def forward_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает сообщения пользователя в группу поддержки или личный аккаунт."""
    if FORWARD_MODE == "support_chat":
        forwarded_msg = await update.message.forward(TELEGRAM_SUPPORT_CHAT_ID)
    elif FORWARD_MODE == "personal_account":
        forwarded_msg = await update.message.forward(PERSONAL_ACCOUNT_CHAT_ID)
    else:
        await update.message.reply_text("Неверный режим пересылки.")
        return

    if forwarded_msg:
        # Сохраняем user_id в контексте бота
        context.bot_data[str(forwarded_msg.message_id)] = update.effective_user.id
        await update.message.reply_text(
            "Ваше сообщение было отправлено. Мы скоро свяжемся с вами!"
        )
        logging.info(
            f"Пересланное сообщение ID: {forwarded_msg.message_id} от пользователя ID: {update.effective_user.id}"
        )
    else:
        await update.message.reply_text(
            "Извините, произошла ошибка при пересылке вашего сообщения. Пожалуйста, попробуйте позже."
        )


async def forward_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает сообщения из группы или личного аккаунта обратно пользователю."""
    logging.info("Вызвана функция forward_to_user")
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        logging.info("Сообщение является ответом на другое сообщение")
        # Извлекаем user_id из bot_data, используя ID оригинального сообщения
        original_message_id = str(update.message.reply_to_message.message_id)
        user_id = context.bot_data.get(original_message_id)
        logging.info(f"Оригинальный ID сообщения: {original_message_id}, ID пользователя: {user_id}")
        if user_id:
            try:
                await context.bot.send_message(
                    chat_id=user_id, text=update.message.text
                )
                await update.message.reply_text(
                    "Сообщение успешно отправлено пользователю."
                )
                # Удаляем сохранённый user_id
                del context.bot_data[original_message_id]
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения пользователю: {str(e)}")
                await update.message.reply_text(
                    f"Ошибка при отправке сообщения пользователю: {str(e)}"
                )
        else:
            logging.warning("Не удалось найти пользователя для ответа.")
            await update.message.reply_text("Не удалось найти пользователя для ответа.")
    else:
        logging.warning("Это сообщение не является ответом на пересланное сообщение.")
        await update.message.reply_text(
            "Это сообщение не является ответом на пересланное сообщение."
        )
