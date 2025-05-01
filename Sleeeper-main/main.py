import os
import logging
from utils import Bot, create_collections
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

create_collections()

bot = Bot()
bot.run(os.getenv("DISCORD_TOKEN"))
