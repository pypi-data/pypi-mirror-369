import socket

class IRCClient():
    def __init__(self, TOKEN: str, NICK: str, CHANNEL: str, SERVER: str = "irc.chat.twitch.tv", PORT: int = 6667):
        """
        Creates an IRC Client config.
        
        Args:
            TOKEN (str): The OAuth token (must start with 'oauth:')
            NICK (str): The bot's Twitch username
            CHANNEL (str): The channel to join (must start with '#')
            SERVER (str): IRC server hostname
            PORT (int): IRC port
        """
        
        if not TOKEN.startswith("oauth:"):
            raise ValueError("OAuth token must start with 'oauth:'")
        if not NICK:
            raise ValueError("Nick cannot be empty.")
        if not CHANNEL.startswith("#"):
            CHANNEL = f"#{CHANNEL}"
        
        self.token = TOKEN
        self.nickname = NICK
        self.channel = CHANNEL
        self.server = SERVER
        self.port = PORT
        self.irc = None
        self.recv_buffer = ""
    
    def connect(self):
        """
        Connects to the IRC Server and joins the specified channel.
        """
        
        self.irc = socket.socket()
        self.irc.connect((self.server, self.port))
        self.irc.settimeout(1)
        
        self.send_raw(f"PASS {self.token}")
        self.send_raw(f"NICK {self.nickname}")
        self.send_raw(f"JOIN {self.channel}")
        
    def send_raw(self, MESSAGE: str):
        """
        Sends a raw message to the IRC Server.
        
        Args:
            MESSAGE (str): The raw IRC message to send
        """
        if not self.irc:
            raise ConnectionError("IRC Connection is not established.")
        
        print(f"[IRC Raw] {MESSAGE}")
        self.irc.send((MESSAGE + "\r\n").encode("utf-8"))
    
    def recv(self, BUFFER_SIZE: int = 2048):
        """
        Receives data from the IRC Server.
        
        Args:
            BUFFER_SIZE (int): The buffer size for receiving data
        """
        if not self.irc:
            raise ConnectionError("IRC Connection is not established.")
        
        while '\r\n' not in self.recv_buffer:
            try:
                CHUNK = self.irc.recv(BUFFER_SIZE).decode("utf-8")
                if not CHUNK:
                    raise ConnectionError("Disconnected from server.")
                self.recv_buffer += CHUNK
            except socket.timeout:
                raise
            
        line, self.recv_buffer = self.recv_buffer.split('\r\n', 1)
        return line
    
    def close(self):
        """
        Closes the IRC Connection.
        """
        if self.irc:
            self.irc.close()
            self.irc = None