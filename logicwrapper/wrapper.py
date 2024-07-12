from dotenv import load_dotenv
from os import getenv

load_dotenv()
DEV_MODE = getenv("DEV_MODE", "False") == "True"

class LogicWrapper:
    def __init__(self):
        pass

    async def send_message(self, message, interaction = None):
        pass

    async def send_dm(self, user_id, message):
        pass

    async def create_thread(self, starter_message):
        pass

    async def create_embed(self, message):
        pass