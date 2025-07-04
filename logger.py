import logging
import os
import asyncio
from telegram import Bot
from telegram.helpers import escape_markdown

class TelegramErrorHandler(logging.Handler):
    MAX_LEN = 4096

    def __init__(self, bot_token, chat_id):
        super().__init__(level=logging.ERROR)
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id

    def emit(self, record):
        try:
            msg = self.format(record)
            safe_msg = escape_markdown(msg, version=2)
            text = f"⚠️ *Bot Error*\n{safe_msg}"

            # Nachricht ggf. in mehrere Stücke aufteilen
            chunks = [text[i:i + self.MAX_LEN] for i in range(0, len(text), self.MAX_LEN)]

            for chunk in chunks:
                asyncio.create_task(
                    self.bot.send_message(
                        chat_id=self.chat_id,
                        text=chunk,
                        parse_mode="MarkdownV2"
                    )
                )
        except Exception:
            self.handleError(record)

def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    logging.basicConfig(format=fmt, level=getattr(logging, log_level, logging.INFO))
    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        level=logging.DEBUG,  # vorher vielleicht INFO
    )


    # File-Handler
    fh = logging.FileHandler("bot.log", encoding="utf-8")
    fh.setLevel(log_level)
    fh.setFormatter(logging.Formatter(fmt))
    logging.getLogger().addHandler(fh)

    # Telegram Error-Handler
    dev_chat = os.getenv("DEVELOPER_CHAT_ID")
    bot_token = os.getenv("BOT_TOKEN")
    if dev_chat and bot_token:
        th = TelegramErrorHandler(bot_token, dev_chat)
        th.setFormatter(logging.Formatter(fmt))
        logging.getLogger().addHandler(th)