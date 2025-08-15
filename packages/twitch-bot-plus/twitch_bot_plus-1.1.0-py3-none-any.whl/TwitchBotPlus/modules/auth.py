import os
import requests

from dotenv import load_dotenv

class Auth:
    def __init__(self, ENV_PATH = None):
        if ENV_PATH is None:
            raise ValueError("ENV_PATH is required but was not provided.")
        
        load_dotenv(ENV_PATH)
        self.env_path = ENV_PATH
        
        self.CLIENT_ID = os.getenv('CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        self.REFRESH_TOKEN = os.getenv('TWITCH_REFRESH_TOKEN')
        self.OAuth_TOKEN = None
        
        self.refresh_access_token()
    
    def refresh_access_token(self):
        payload = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'refresh_token': self.REFRESH_TOKEN,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post('https://id.twitch.tv/oauth2/token', data=payload)
        if response.status_code != 200:
            raise Exception(f'Failed to refresh token: {response.text}')
        
        data = response.json()
        self.OAuth_TOKEN = f"oauth:{data['access_token']}"
        self.REFRESH_TOKEN = data['refresh_token']

        self._update_env_file()
        self._update_runtime_env()
        
    def _update_env_file(self):
        with open(self.env_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(self.env_path, 'w', encoding='utf-8') as file:
            for line in lines:
                if line.startswith('TWITCH_OAUTH='):
                    file.write(f'TWITCH_OAUTH={self.OAuth_TOKEN}\n')
                elif line.startswith('TWITCH_REFRESH_TOKEN='):
                    file.write(f'TWITCH_REFRESH_TOKEN={self.REFRESH_TOKEN}\n')
                else:
                    file.write(line)

    def _update_runtime_env(self):
        if self.OAuth_TOKEN is not None:
            os.environ['TWITCH_OAUTH'] = self.OAuth_TOKEN
        if self.REFRESH_TOKEN is not None:
            os.environ['TWITCH_REFRESH_TOKEN'] = self.REFRESH_TOKEN

    def get_oauth_token(self):
        return self.OAuth_TOKEN