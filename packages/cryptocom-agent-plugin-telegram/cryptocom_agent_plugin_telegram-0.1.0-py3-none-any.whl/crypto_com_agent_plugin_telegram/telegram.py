import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

from crypto_com_agent_client.plugins.base import AgentPlugin

logger = logging.getLogger(__name__)


class TelegramPlugin(AgentPlugin):
    mode = "primary"

    """
    Telegram bot plugin for the Crypto.com Agent system.

    This plugin allows users to interact with the agent via Telegram.
    It handles command registration, message forwarding, and supports both short and long message replies.

    Features:
        - Registers `/start` and text message handlers
        - Routes user input to the Agent interaction handler
        - Handles long responses by splitting them across multiple messages
        - Supports `.run()` lifecycle hook for polling loop execution
    """

    def __init__(self, bot_token: str):
        """
        Initialize the Telegram plugin.

        Args:
            bot_token (str): Telegram bot token obtained from BotFather.
        """
        self.bot_token = bot_token
        self.application = None
        self.handler = None  # Will be injected by the agent at runtime

    def setup(self, handler):
        """
        Setup the Telegram bot with command and message handlers.

        Args:
            handler: An instance of InteractionHandler provided by the Agent.
        """
        logger.info("[TelegramPlugin] Setting up...")
        self.handler = handler
        self.application = Application.builder().token(self.bot_token).build()

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        logger.info("[TelegramPlugin] Setup complete.")

    async def start(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for the /start command.

        Args:
            update (Update): Incoming Telegram update.
            context (CallbackContext): Context provided by the Telegram library.
        """
        try:
            await update.message.reply_text(
                "Hello! I am your Crypto.com AI Agent. Send me a message to interact!"
            )
        except Exception as e:
            logger.error(f"[TelegramPlugin/start] Error: {e}")
            await update.message.reply_text("An error occurred. Please try again.")

    async def handle_message(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for incoming text messages.

        Args:
            update (Update): Incoming message update from the user.
            context (CallbackContext): Telegram context for handling replies.
        """
        try:
            user_message = update.message.text
            chat_id = update.message.chat_id
            response = self.handler.interact(user_message, thread_id=chat_id)

            MAX_MESSAGE_LENGTH = 4096
            if len(response) > MAX_MESSAGE_LENGTH:
                for i in range(0, len(response), MAX_MESSAGE_LENGTH):
                    await update.message.reply_text(
                        response[i : i + MAX_MESSAGE_LENGTH]
                    )
            else:
                await update.message.reply_text(response)

        except Exception as e:
            logger.error(f"[TelegramPlugin/handle_message] Error: {e}")
            await update.message.reply_text(
                "An error occurred while processing your request."
            )

    def run(self):
        """
        Starts the Telegram polling loop.

        This method blocks the main thread and listens for incoming Telegram messages.
        """
        logger.info("[TelegramPlugin] Starting polling loop...")
        try:
            self.application.run_polling()
        except KeyboardInterrupt:
            logger.info("[TelegramPlugin] Stopped by user")
        except Exception as e:
            logger.error(f"[TelegramPlugin/run] Error: {e}")
        finally:
            logger.info("[TelegramPlugin] Shutdown complete")
