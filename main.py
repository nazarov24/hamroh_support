import logging
import signal
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import start, forward_to_group, forward_to_user
from settings import TELEGRAM_TOKEN, TELEGRAM_SUPPORT_CHAT_ID, PERSONAL_ACCOUNT_CHAT_ID

# Configure logging
logging.basicConfig(level=logging.INFO)

async def shutdown(application: Application):
    """Gracefully shut down the application."""
    logging.info("Received stop signal, shutting down...")
    await application.shutdown()

def main():
    # Initialize bot and application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND
            & ~filters.Chat(
                chat_id=[TELEGRAM_SUPPORT_CHAT_ID, PERSONAL_ACCOUNT_CHAT_ID]
            ),
            forward_to_group,
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT
            & filters.Chat(chat_id=[TELEGRAM_SUPPORT_CHAT_ID, PERSONAL_ACCOUNT_CHAT_ID])
            & filters.REPLY,
            forward_to_user,
        )
    )

    logging.info("Handlers registered.")

    # Set up signal handlers for graceful shutdown
    application.run_polling(stop_signals=(signal.SIGINT, signal.SIGTERM))

if __name__ == "__main__":
    main()
