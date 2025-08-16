from typing import Any, Union, Optional

class StateManager:
    def __init__(self):
        self.states: dict[str, Any] = {}
        self.datas: dict[str, dict[str, Any]] = {}

    def set_state(self, user_id: str, state: Any):
        self.states[user_id] = state
    
    def get_state(self, user_id: str):
        return self.states.get(user_id)
    
    def clear_state(self, user_id: str):
        self.states.pop(user_id, None)
    
    def set_data(self, user_id: str, **data):
        if user_id not in self.datas:
            self.datas[user_id] = {}
        self.datas[user_id].update(data)
        
    def get_data(self, user_id: str, key: Optional[Union[str, int]] = None):
        if key is not None:
            return self.datas.get(user_id, {}).get(key)
        return self.datas.get(user_id)
    
    def clear_data(self, user_id: str):
        self.datas.pop(user_id, None)

state_manager = StateManager()