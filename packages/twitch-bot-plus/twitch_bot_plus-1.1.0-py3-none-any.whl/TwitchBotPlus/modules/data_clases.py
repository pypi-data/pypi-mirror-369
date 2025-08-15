from dataclasses import dataclass
from typing import Any

@dataclass
class CommandInfo:
    command: str
    args: list[str]
    user: str

@dataclass
class CommandData:
    irc: Any
    channel: str
    command_info: CommandInfo