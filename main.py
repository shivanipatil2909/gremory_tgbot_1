# main.py

import logging
import time
from telegram_api.api import get_updates
from handlers.commands import handle_start, handle_message
from handlers.callbacks import handle_callback
from utils.state_manager import user_states

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting bot...")

    offset = None  # Initial offset

    while True:
        try:
            logger.info("Polling for updates...")
            updates_response = get_updates(offset, timeout=60)

            if not updates_response or not updates_response.get("ok"):
                logger.warning(f"No valid updates or error: {updates_response}")
                time.sleep(5)
                continue

            for update in updates_response.get("result", []):
                if "message" in update:
                    message = update["message"]
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")
                    from_user = message.get("from", {})
                    first_name = from_user.get("first_name", "User")
                    username = from_user.get("username")

                    if text.startswith("/start"):
                        handle_start(chat_id, first_name, username)
                    else:
                        handle_message(chat_id, text)

                elif "callback_query" in update:
                    handle_callback(update["callback_query"])

                offset = update["update_id"] + 1  # Update offset

            time.sleep(1)  # Avoid API spamming

        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            time.sleep(5)

if __name__ == '__main__':
    main()
