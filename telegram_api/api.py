# telegram_api/api.py

import os
import json
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

logger = logging.getLogger(__name__)

def send_message(chat_id, text, reply_markup=None):
    url = f"{API_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)

    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

def answer_callback_query(callback_query_id):
    url = f"{API_URL}/answerCallbackQuery"
    payload = {'callback_query_id': callback_query_id}

    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        logger.error(f"Error answering callback: {e}")
        return None

def edit_message_text(chat_id, message_id, text, reply_markup=None):
    url = f"{API_URL}/editMessageText"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)

    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        return None

def get_updates(offset=None, timeout=30):
    url = f"{API_URL}/getUpdates"
    payload = {'timeout': timeout}

    if offset:
        payload['offset'] = offset

    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        return None
