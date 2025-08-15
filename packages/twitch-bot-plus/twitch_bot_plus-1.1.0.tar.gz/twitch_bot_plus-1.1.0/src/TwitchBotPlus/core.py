# From Imports
from .modules import IRCClient, Auth, cmd_handler, GetUsername, CommandData, CommandInfo
from dotenv import load_dotenv
from typing import cast

# Normal Imports
import os, threading, queue, socket

# <!-------< Main >-------!>
class Bot:
    def __init__(self, COMMANDS: dict ,ENV_Path = None, HANDLE: str = "!"):
        """
        Initialize the Twitch Bot
        
        Args:
            COMMANDS (dict): Example, {"add": add, "subtract": subtract}
            ENV_Path (str): While it's not required you should put your env file location so you can auto-update the OAuth details
            HANDLE (str): The command handle such as; '-help', '-hello', '-test'
        """
        load_dotenv()
        auth = Auth(ENV_PATH=ENV_Path)
        
        self.name = cast(str, os.getenv("BOTNAME"))
        self.token = cast(str, auth.get_oauth_token())
        self.channel = cast(str, os.getenv("CHANNEL"))
        
        self.handle = HANDLE
        self.commands = COMMANDS
        
        self.shutdown_requested = threading.Event()
        self.command_queue = queue.Queue()
        
        missing = [var for var, value in {
            "BOTNAME": self.name,
            "TOKEN": self.token,
            "CHANNEL": self.channel
        }.items() if not value]

        if missing:
            raise ValueError(f"Missing required environment variable(s): {', '.join(missing)}")
        
        self.irc = IRCClient(self.token, self.name, self.channel)
        self.irc.connect()
    
    def start(self):
        threading.Thread(
            target=self.worker,
            daemon=True
        ).start()
        self.main()
    
    def worker(self):
        while True:
            data = self.command_queue.get()
            
            if data is None:
                print("[WORKER] Shutdown signal received!")
                self.command_queue.task_done()
                break
            
            try:
                shutdown_request = cmd_handler(
                    data=data, 
                    COMMANDS=self.commands,
                    handle=self.handle
                )
                if shutdown_request:
                    self.shutdown_requested.set()
            except Exception as e:
                print(f"[WORKER] Error: {e}")
            finally:
                self.command_queue.task_done()
    
    def handle_message(self, RESPONSE: str):
        if "PRIVMSG" not in RESPONSE:
            return
        
        parts = RESPONSE.split(":", 2)
        if len(parts) < 3:
            return
        
        FULL_MSG = parts[2].strip()
        user = GetUsername(RESPONSE)
        words = FULL_MSG.split()
        
        if not words:
            return
        
        command = words[0].lower()
        args = words[1:]
        
        #self.command_queue.put((self.irc, self.channel, (command, args, user)))
        self.command_queue.put(
            CommandData(
                irc=self.irc,
                channel=self.channel,
                command_info=CommandInfo(
                    command=command,
                    args=args,
                    user=user
                )
            )
        )
    
    def main(self):
        print(f"[BOT] {self.name} is warming up...")
        
        try:
            while True:
                if self.shutdown_requested.is_set():
                    break
                
                try:
                    response = self.irc.recv()
                except socket.timeout as s:
                    if self.shutdown_requested.is_set():
                        print(f"[MAIN] Socket Timeout: {s}")
                        break
                    continue
                except Exception as e:
                    print(f"[Main] Error: {e}")
                    continue
                
                if response.startswith("PING"):
                    self.irc.send_raw("PONG :tmi.twitch.tv")
                else:
                    self.handle_message(response)
        finally:
            print(f"[BOT] Cleaning up after {self.name}...")
            self.command_queue.put(None)
            self.command_queue.join()
            self.irc.close()
            print(f"[BOT] Shutdown of {self.name} has been completed.")