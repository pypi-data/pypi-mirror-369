import os

from dotenv import load_dotenv, set_key
from platformdirs import user_config_dir

config_dir = user_config_dir("hub_to_lab")
os.makedirs(config_dir, exist_ok=True)

ENV_FILE = os.path.join(config_dir, ".env")
load_dotenv(ENV_FILE)

def update_env_variable(key: str, value: str):

    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'w') as f:
            pass
    set_key(ENV_FILE, key, value)
