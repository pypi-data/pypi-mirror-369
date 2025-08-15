# loggerXio/core.py
import sys
import logging
import threading
import telebot


class TelebotLogHandler(logging.Handler):
    """Custom logging handler to send logs to Telegram via Telebot."""

    def __init__(self, bot_token, chat_id):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.tb = telebot.TeleBot(bot_token, parse_mode="HTML")

    def emit(self, record):
        log_entry = self.format(record)
        safe_msg = f"<code>{log_entry}</code>"
        threading.Thread(
            target=lambda: self.tb.send_message(self.chat_id, safe_msg),
            daemon=True
        ).start()


def setup_logger(bot_token: str,
                 chat_id: int,
                 level=logging.INFO,
                 time=True,
                 show_logs=True,
                 fetch_print=True,
                 level_info=True):
    """
    Set up logger with optional timestamp, console visibility, print capturing,
    and level-based control.

    Args:
        bot_token (str): Telegram bot token for sending logs
        chat_id (int): Telegram chat ID to send logs to
        level (int): Logging level (default=logging.INFO)
        time (bool): Include timestamp in logs
        show_logs (bool): Also print logs to console
        fetch_print (bool): Capture print() output and send to Telegram
        level_info (bool): Use logging levels (True) or only capture prints (False)
    """
    log_format = "[%(asctime)s] - %(levelname)s\n%(message)s" if time else "%(levelname)s\n%(message)s"

    if level_info:
        logging.basicConfig(level=level, format=log_format)
        telebot_handler = TelebotLogHandler(bot_token, chat_id)
        telebot_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(telebot_handler)

        if show_logs:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(log_format))
            logging.getLogger().addHandler(console_handler)

    if fetch_print or not level_info:
        class TelebotWriter:
            def write(self, message):
                if message.strip():
                    safe_msg = f"<code>{message.strip()}</code>"
                    threading.Thread(
                        target=lambda: telebot_handler.tb.send_message(chat_id, safe_msg)
                        if level_info else telebot.TeleBot(bot_token, parse_mode="HTML").send_message(chat_id, safe_msg),
                        daemon=True
                    ).start()
                if show_logs:
                    sys.__stdout__.write(message + "\n")

            def flush(self):
                pass

        sys.stdout = TelebotWriter()
        sys.stderr = TelebotWriter()

    return logging.getLogger()
