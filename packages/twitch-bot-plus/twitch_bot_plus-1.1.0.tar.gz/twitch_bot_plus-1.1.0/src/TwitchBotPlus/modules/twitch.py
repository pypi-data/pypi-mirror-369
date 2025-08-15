def Send(irc, CHANNEL: str, MESSAGE: str):
    """
    Sends a message to the specified IRC Channel.
    
    Args:
        irc (socket): The active IRC Socket connection
        CHANNEL (str): The Twitch channel to send the message to (Must start with '#')
        MESSAGE (str): The message content
    """
    if not CHANNEL.startswith("#"):
        CHANNEL = f"#{CHANNEL}"
    
    if hasattr(irc, "send_raw"):
        irc.send_raw(f"PRIVMSG {CHANNEL} :{MESSAGE}")
    else:
        irc.send(f"PRIVMSG {CHANNEL} :{MESSAGE}\r\n".encode("utf-8"))

def GetUsername(raw: str) -> str:
    """
    Extracts the sender's username from the raw IRC message.
    
    Args:
        raw (str): Raw IRC PRIVMSG string
    """
    return raw.split("!", 1)[0][1:]