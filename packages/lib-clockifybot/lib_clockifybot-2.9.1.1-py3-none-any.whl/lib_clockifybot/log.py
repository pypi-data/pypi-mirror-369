import logging
import os

from elasticapm import Client
from telebot import TeleBot


def add_log(the_error, username=None, file_path=None):
    log_channel_id = str(os.getenv("LOG_CHANNEL_ID"))
    current_dir = os.path.dirname(os.getenv("CLOCKIFY_LOG_DIR"))
    logging_bot = TeleBot(os.getenv("TOKEN_LOGGING"))
    report_username = TeleBot(os.getenv("TOKEN_REPORT")).get_me().username
    username = report_username if username is None else username
    log_filename = os.path.join(current_dir, f"{username}_logs.log")
    logging.basicConfig(
        filename=log_filename,
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.error(the_error)
    logging_bot.send_message(log_channel_id, f"{username} - {the_error}")
    try:
        if file_path:
            with open(file_path, "rb") as file:
                logging_bot.send_document(os.getenv("BACKUP_CHANNEL_ID"), file)
    except Exception as e:
        logging_bot.send_message(log_channel_id, f"Error in sending Backup - {e}")


def log_to_elasticsearch(message, bot):
    if os.getenv("ELK_API") is None:
        return
    apm = Client(
        service_name=bot.get_me().username,
        server_url=os.getenv("ELK_URL"),
        secret_token=os.getenv("ELK_API"),
    )
    log_entry = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "message": message.text,
        "timestamp": message.date,
    }
    apm.capture_message(message.text, custom=log_entry)
