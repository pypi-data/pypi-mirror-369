from dataclasses import dataclass
from typing import Any, Callable
from .twitch import Send

# Data Classes
@dataclass
class CommandInfo:
    command: str
    args: list[str]
    user: str
    
    def __iter__(self):
        yield self.command
        yield self.args
        yield self.user

@dataclass
class CommandData:
    irc: Any
    channel: str
    command_info: CommandInfo
    
    def __iter__(self):
        yield self.irc
        yield self.channel
        yield self.command_info

# Main function
def cmd_handler(
        data: CommandData,
        COMMANDS: dict[str, Callable[[list[str], str], Any]],
        handle: str
    ) -> bool:
    """
    Handles every user message sent.
    
    Args:
        data: (irc, channel, command_info) — where command_info is (command, args, user).
        commands: Mapping of command names to callables.
    """
    
    irc = data.irc
    channel = data.channel
    info = data.command_info

    command = info.command
    args = info.args
    user = info.user

    if not command.startswith(handle):
        return False

    cmd = command[len(handle):].lower()
    
    if cmd in COMMANDS:
        try:
            result, shutdown = COMMANDS[cmd](args, user)
            if result is not None:
                Send(
                    irc=irc,
                    CHANNEL=channel,
                    MESSAGE=result
                )
                return shutdown
        except Exception as e:
            print(f"Error executing command '{cmd}': {e}")
    
    return False