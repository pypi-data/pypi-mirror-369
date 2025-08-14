# rubox/filters.py

# rubox/filters.py
from typing import Callable, Any, Optional, Union, List
from dataclasses import dataclass

@dataclass
class Filter:
    condition: Callable[[Any], bool]

    def __call__(self, message: dict) -> bool:
        return self.condition(message)

    def __and__(self, other):
        return Filter(lambda m: self(m) and other(m))

    def __or__(self, other):
        return Filter(lambda m: self(m) or other(m))

def commands(values: Union[str, List[str]]) -> Filter:
    if isinstance(values, str):
        values = [values]

    def check_command(message: dict) -> bool:
        message_text = message.get("text", "").strip()
        if not message_text.startswith("/"):
            return False
        
        command_parts = message_text[1:].split(maxsplit=1)
        if not command_parts:
            return False
            
        command = command_parts[0].lower()
        
        normalized_values = [v[1:].lower() if v.startswith('/') else v.lower() for v in values]
        return command in normalized_values
        
    return Filter(check_command)

def text(value: str) -> Filter:
    return Filter(lambda m: m.get("text", "").lower() == value.lower())

def chat_type(value: str) -> Filter:
    return Filter(lambda m: m.get("chat_type", "") == value)

def inline_button_id(value: str) -> Filter:
    return Filter(lambda m: m.get("button_id", "") == value)

def private():
    return Filter(lambda msg: msg.get("sender_type") == "User")

def inline_data(value: str) -> Filter:
    return Filter(lambda m: m.get("data", "") == value)

def location():
    return Filter(lambda msg: "location" in msg)

def sticker():
    return Filter(lambda msg: "sticker" in msg)

def file():
    return Filter(lambda msg: "file" in msg)

def contact():
    return Filter(lambda msg: "contact_message" in msg)