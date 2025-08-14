import os

import requests
from dotenv import load_dotenv, set_key

ENV_FILE = ".env"
load_dotenv(ENV_FILE)

def update_env_variable(key: str, value: str):

    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'w') as f:
            pass
    set_key(ENV_FILE, key, value)
