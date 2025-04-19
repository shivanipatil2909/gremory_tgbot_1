# telegram_api/buttons.py

def create_main_menu_buttons():
    return {
        "inline_keyboard": [
            [{"text": "👥 My Agents", "callback_data": "show_agents"}],
            [{"text": "💼 Portfolio", "callback_data": "portfolio"}],
            [{"text": "🔍 Explore Pools", "callback_data": "explore_pools"}]
        ]
    }

def create_agent_menu_buttons():
    return {
        "inline_keyboard": [
            [{"text": "➕ Deploy New Agent", "callback_data": "deploy_agent"}],
            [{"text": "⬅️ Back to Main Menu", "callback_data": "main_menu"}]
        ]
    }

def create_pools_menu_buttons(current_offset=0, total_count=0):
    prev_button = {"text": "⬅️ Previous", "callback_data": f"prev_pools:{current_offset - 5}"}
    next_button = {"text": "➡️ Next", "callback_data": f"next_pools:{current_offset + 5}"}

    if current_offset == 0:
        prev_button["callback_data"] = "no_action"
    if current_offset + 5 >= total_count:
        next_button["callback_data"] = "no_action"

    return {
        "inline_keyboard": [
            [prev_button, next_button],
            [{"text": "🔍 Search Pool", "callback_data": "search_pool"}],
            [{"text": "⬅️ Back to Main Menu", "callback_data": "main_menu"}]
        ]
    }

def create_back_button():
    return {
        "inline_keyboard": [
            [{"text": "⬅️ Back", "callback_data": "back"}]
        ]
    }
