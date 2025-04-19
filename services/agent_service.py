import uuid
from datetime import datetime
from .user_service import add_agent_to_user, get_user_by_chat_id, get_user_agent_ids
from .pool_service import search_pool

# In-memory agent database
agents_db = {}

def create_agent(chat_id, agent_name, pool_name, initial_investment, min_price, max_price):
    pool_details = search_pool(pool_name)
    if pool_details.startswith("❌"):
        return False, "Failed to fetch pool details"

    agent_id = str(uuid.uuid4())[:8]
    agent = {
        "id": agent_id,
        "name": agent_name,
        "pool_name": pool_name,
        "initial_investment": float(initial_investment),
        "current_investment": float(initial_investment),
        "min_price": float(min_price),
        "max_price": float(max_price),
        "created_at": datetime.now().isoformat(),
        "last_rebalance": datetime.now().isoformat(),
        "total_rebalances": 0,
        "fees_earned": 0.0,
        "status": "deployed"
    }

    agents_db[agent_id] = agent
    add_agent_to_user(chat_id, agent_id)
    return True, agent

def get_user_agents(chat_id):
    agent_ids = get_user_agent_ids(chat_id)
    return [agents_db[aid] for aid in agent_ids if aid in agents_db]

def get_agent_details(agent_id):
    return agents_db.get(agent_id)

def get_user_portfolio(chat_id):
    user = get_user_by_chat_id(chat_id)
    if not user:
        return None

    agents = get_user_agents(chat_id)
    total_investment = sum(a["initial_investment"] for a in agents)
    current_value = sum(a["current_investment"] for a in agents)
    total_fees = sum(a["fees_earned"] for a in agents)
    active_agents = sum(1 for a in agents if a["status"] == "deployed")

    return {
        "first_name": user.get("first_name", "User"),
        "total_investment": total_investment,
        "current_value": current_value,
        "profit_loss": current_value - total_investment,
        "total_fees_earned": total_fees,
        "active_agents": active_agents,
        "total_agents": len(agents)
    }
