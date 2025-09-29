import logging
import os

from dotenv import load_dotenv

from src.discord_client import *

from src.commands.card import *
from src.commands.glossary import *


logging.basicConfig(level=logging.INFO)

load_dotenv()

TOKEN: str = os.getenv("TOKEN") or ""


if __name__ == "__main__":
    client.run(TOKEN, log_level=logging.INFO)
