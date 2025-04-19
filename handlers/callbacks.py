from telegram_api.api import answer_callback_query, edit_message_text
from services.user_service import get_user_by_chat_id
from services.agent_service import get_user_agents, get_user_portfolio
from services.pool_service import fetch_pools
from telegram_api.buttons import (
    create_main_menu_buttons,
    create_agent_menu_buttons,
    create_pools_menu_buttons,
    create_back_button
)
from utils.state_manager import user_states

def handle_callback(callback_query):
    query_id = callback_query.get("id")
    data = callback_query.get("data")
    message = callback_query.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    answer_callback_query(query_id)
    user = get_user_by_chat_id(chat_id)

    if not user and data != "back":
        edit_message_text(chat_id, message_id, "Session expired. Please restart the bot with /start command.")
        return

    if data == "main_menu":
        user_states.pop(str(chat_id), None)
        edit_message_text(chat_id, message_id, f"Main Menu - Welcome {user.get('first_name', 'User')}!", create_main_menu_buttons())

    elif data == "show_agents":
        agents = get_user_agents(chat_id)
        if not agents:
            edit_message_text(chat_id, message_id, "You don't have any agents yet. Deploy one to start trading!", create_agent_menu_buttons())
        else:
            text = f"🤖 Your Trading Agents ({len(agents)}):\n\n"
            for agent in agents:
                pl = agent["current_investment"] - agent["initial_investment"]
                perc = (pl / agent["initial_investment"]) * 100 if agent["initial_investment"] else 0
                text += (
                    f"Name: {agent['name']}\n"
                    f"Pool: {agent['pool_name']}\n"
                    f"Investment: ${agent['initial_investment']:,.2f}\n"
                    f"Current: ${agent['current_investment']:,.2f}\n"
                    f"P/L: ${pl:,.2f} ({perc:.2f}%)\n"
                    f"Fees: ${agent['fees_earned']:,.2f}\n"
                    f"Status: {agent['status'].upper()}\n\n"
                )
            edit_message_text(chat_id, message_id, text, create_agent_menu_buttons())

    elif data == "deploy_agent":
        user_states[str(chat_id)] = {"state": "deploy_agent_name"}
        edit_message_text(chat_id, message_id, "Let's deploy a new trading agent! First, what would you like to name your agent?")

    elif data == "portfolio":
        portfolio = get_user_portfolio(chat_id)
        if not portfolio:
            edit_message_text(chat_id, message_id, "Failed to retrieve portfolio information.", create_main_menu_buttons())
            return

        pl = portfolio["profit_loss"]
        perc = (pl / portfolio["total_investment"]) * 100 if portfolio["total_investment"] else 0

        msg = (
            f"💼 Portfolio Summary for {portfolio['first_name']}\n\n"
            f"Total Investment: ${portfolio['total_investment']:,.2f}\n"
            f"Current Value: ${portfolio['current_value']:,.2f}\n"
            f"Profit/Loss: ${pl:,.2f} ({perc:.2f}%)\n"
            f"Fees Earned: ${portfolio['total_fees_earned']:,.2f}\n"
            f"Active Agents: {portfolio['active_agents']}/{portfolio['total_agents']}"
        )

        edit_message_text(chat_id, message_id, msg, create_main_menu_buttons())

    elif data == "explore_pools":
        pools_msg, count, total = fetch_pools(5, 0)
        edit_message_text(chat_id, message_id, pools_msg, create_pools_menu_buttons(0, total))

    elif data.startswith("prev_pools:") or data.startswith("next_pools:"):
        offset = int(data.split(":")[1])
        offset = max(0, offset)
        pools_msg, count, total = fetch_pools(5, offset)
        if count == 0 and offset > 0:
            offset = max(0, offset - 5)
            pools_msg, _, total = fetch_pools(5, offset)
        edit_message_text(chat_id, message_id, pools_msg, create_pools_menu_buttons(offset, total))

    elif data == "search_pool":
        user_states[str(chat_id)] = {"state": "awaiting_search_pool"}
        edit_message_text(chat_id, message_id, "🔍 Please enter the pool name you want to search:")

    elif data == "back":
        user_state = user_states.get(str(chat_id))
        user_states.pop(str(chat_id), None)
        if user_state and user_state.get("state", "").startswith("deploy_agent"):
            edit_message_text(chat_id, message_id, "Agent deployment cancelled.", create_agent_menu_buttons())
        elif user_state and user_state.get("state") == "awaiting_search_pool":
            pools_msg, _, total = fetch_pools(5, 0)
            edit_message_text(chat_id, message_id, pools_msg, create_pools_menu_buttons(0, total))
        else:
            if user:
                edit_message_text(chat_id, message_id, f"Main Menu - Welcome {user.get('first_name', 'User')}!", create_main_menu_buttons())
            else:
                edit_message_text(chat_id, message_id, "Please restart the bot with /start command.")

    elif data == "no_action":
        pass  # no-op

    else:
        edit_message_text(chat_id, message_id, "⚠️ Unknown option.")
