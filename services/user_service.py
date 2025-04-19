from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# In-memory user database
users_db = {}

def save_user(chat_id, first_name, username=None):
    chat_id_str = str(chat_id)
    if chat_id_str in users_db:
        logger.info(f"User already exists: {chat_id_str}")
        return users_db[chat_id_str]

    user_data = {
        "chat_id": chat_id_str,
        "first_name": first_name,
        "username": username,
        "registered_on": datetime.now().isoformat(),
        "agents": []
    }

    users_db[chat_id_str] = user_data
    logger.info(f"New user saved: {chat_id_str} - {first_name}")
    return user_data

def get_user_by_chat_id(chat_id):
    return users_db.get(str(chat_id))

def add_agent_to_user(chat_id, agent_id):
    chat_id_str = str(chat_id)
    if chat_id_str not in users_db:
        save_user(chat_id, "User")
    users_db[chat_id_str]["agents"].append(agent_id)

def get_user_agent_ids(chat_id):
    user = users_db.get(str(chat_id))
    return user.get("agents", []) if user else []
