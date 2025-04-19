# Simple in-memory state manager
user_states = {}

# Example usage:
# user_states[chat_id] = {
#     "state": "deploy_agent_name",
#     "agent_name": "My Agent"
# }

def get_state(chat_id):
    return user_states.get(str(chat_id))

def set_state(chat_id, state_data):
    user_states[str(chat_id)] = state_data

def clear_state(chat_id):
    user_states.pop(str(chat_id), None)
