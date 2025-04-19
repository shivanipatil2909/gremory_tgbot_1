from services.user_service import save_user, get_user_by_chat_id
from telegram_api.api import send_message
from telegram_api.buttons import create_main_menu_buttons
from utils.state_manager import user_states
from services.pool_service import search_pool
from telegram_api.buttons import create_pools_menu_buttons, create_back_button
from services.agent_service import create_agent
from telegram_api.buttons import create_agent_menu_buttons

def handle_start(chat_id, first_name, username=None):
    save_user(chat_id, first_name, username)
    user_states.pop(str(chat_id), None)

    send_message(
        chat_id,
        f"Welcome to the Meteora Trading Bot, {first_name}! What would you like to do today?",
        create_main_menu_buttons()
    )

def handle_message(chat_id, text):
    user = get_user_by_chat_id(chat_id)
    user_state = user_states.get(str(chat_id))

    if not user:
        send_message(chat_id, "Please start the bot with /start command first.")
        return

    # State-based input routing
    if user_state and user_state.get("state") == "awaiting_search_pool":
        pool_name = text.strip()
        pool_details = search_pool(pool_name)
        user_states.pop(str(chat_id), None)
        send_message(chat_id, pool_details, create_pools_menu_buttons())

    elif user_state and user_state.get("state") == "deploy_agent_name":
        agent_name = text.strip()
        user_states[str(chat_id)] = {
            "state": "deploy_agent_pool",
            "agent_name": agent_name
        }
        send_message(chat_id, f"Great! Your agent will be named '{agent_name}'. Now, which pool should this agent trade on? (e.g., SOL-USDC)")

    elif user_state and user_state.get("state") == "deploy_agent_pool":
        pool_name = text.strip()
        agent_name = user_state.get("agent_name", "New Agent")
        pool_check = search_pool(pool_name)

        if pool_check.startswith("❌"):
            send_message(chat_id, f"Sorry, I couldn't find a pool named '{pool_name}'. Please try again with a valid pool name.", create_back_button())
            return

        user_states[str(chat_id)] = {
            "state": "deploy_agent_investment",
            "agent_name": agent_name,
            "pool_name": pool_name
        }

        send_message(chat_id, f"Pool '{pool_name}' found! How much would you like to invest in this agent? (in USD, e.g., 1000)")

    elif user_state and user_state.get("state") == "deploy_agent_investment":
        try:
            investment = float(text.strip())
            if investment <= 0:
                raise ValueError("Investment must be positive")

            user_states[str(chat_id)]["investment"] = investment
            send_message(chat_id, f"You'll invest ${investment:,.2f}. Now, what's the minimum price at which your agent should trade? (e.g., 20.5)")
            user_states[str(chat_id)]["state"] = "deploy_agent_min_price"

        except ValueError:
            send_message(chat_id, "Please enter a valid number for investment amount.", create_back_button())

    elif user_state and user_state.get("state") == "deploy_agent_min_price":
        try:
            min_price = float(text.strip())
            if min_price <= 0:
                raise ValueError("Min price must be positive")

            user_states[str(chat_id)]["min_price"] = min_price
            send_message(chat_id, f"Minimum price set to ${min_price:,.2f}. Finally, what's the maximum price at which your agent should trade? (e.g., 30.5)")
            user_states[str(chat_id)]["state"] = "deploy_agent_max_price"

        except ValueError:
            send_message(chat_id, "Please enter a valid number for minimum price.", create_back_button())

    elif user_state and user_state.get("state") == "deploy_agent_max_price":
        try:
            max_price = float(text.strip())
            if max_price <= 0:
                raise ValueError("Max price must be positive")

            state = user_state
            if max_price <= state["min_price"]:
                send_message(chat_id, f"Max price (${max_price:,.2f}) must be greater than min price (${state['min_price']:,.2f}).", create_back_button())
                return

            success, result = create_agent(
                chat_id,
                state["agent_name"],
                state["pool_name"],
                state["investment"],
                state["min_price"],
                max_price
            )

            user_states.pop(str(chat_id), None)

            if success:
                agent = result
                msg = (
                    f"🤖 Agent Deployed Successfully!\n\n"
                    f"Name: {agent['name']}\n"
                    f"Pool: {agent['pool_name']}\n"
                    f"Investment: ${agent['initial_investment']:,.2f}\n"
                    f"Price Range: ${agent['min_price']:,.2f} - ${agent['max_price']:,.2f}\n"
                    f"Status: {agent['status'].upper()}\n\n"
                    f"Your agent is now active and will start trading automatically!"
                )
                send_message(chat_id, msg, create_agent_menu_buttons())
            else:
                send_message(chat_id, f"Failed to deploy agent: {result}", create_agent_menu_buttons())

        except ValueError:
            send_message(chat_id, "Please enter a valid number for maximum price.", create_back_button())

    else:
        send_message(chat_id, "I'm not sure what you're asking. Please use the menu buttons to navigate.", create_main_menu_buttons())
