from rubigram.types import Update, InlineMessage
# from rubigram.state import state_manager
from typing import Union
import re


# def state(states: Union[str, list[str]]):
#     def filter(message: Union[Update, InlineMessage]):
#         user_state = state_manager.get_state(message.chat_id)
#         return user_state in states if isinstance(states, list) else user_state == states
#     return filter

def command(commands: Union[str, list[str]], prefix: str = "/"):
    def filter(message: Update):
        if isinstance(message, Update) and message.new_message and message.new_message.text:
            text = message.new_message.text.strip()
            cmds = commands if isinstance(commands, list) else [commands]
            for cmd in cmds:
                if text.lower().startswith(prefix + cmd.lower()):
                    return True
        return False
    return filter

def button(id: Union[str, list[str]]):
    def filter(message: InlineMessage):
        if isinstance(message, InlineMessage):
            button_id = message.aux_data.button_id
            ID = id if isinstance(id, list) else [id]
            for i in ID:
                if button_id == i:
                    return True
        return False
    return filter

def chat(chat_id: Union[str, list[str]]):
    def filter(message: Union[Update, InlineMessage]):
        chat_ids = chat_id if isinstance(chat_id, list) else [chat_id]
        if isinstance(message, Update) or isinstance(message, InlineMessage):
            return message.chat_id in chat_ids
        return False
    return filter

def regex(pattern: str):
    def filter(message: Union[Update, InlineMessage]):
        if isinstance(message, Update) and message.type == "NewMessage" and message.new_message.text:
            return bool(re.search(pattern, message.new_message.text))
        elif isinstance(message, InlineMessage) and message.text:
            return bool(re.search(pattern, message.text))
        return False
    return filter
            
def text():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return message.new_message.text is None
        return False
    return filter

def file():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return message.new_message.file is None
        return False
    return filter

def private():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return message.new_message.sender_type in ["User", "Bot"]
        return False
    return filter

def forward():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return message.new_message.forwarded_from is None
        return False
    return filter

def location():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return message.new_message.location is None
        return False
    return filter

def sticker():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return message.new_message.sticker is None
        return False
    return filter

def contact():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return message.new_message.contact_message is None
        return False
    return filter

def poll():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return message.new_message.poll is None
        return False
    return filter

def live():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return message.new_message.live_location is None
        return False
    return filter