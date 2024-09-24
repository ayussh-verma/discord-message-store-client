from loguru import logger

from client.bot import BOT
from client.config import Config

with logger.catch(message="Unexpected error", level="CRITICAL", reraise=True):
    BOT.run(Config.BOT_TOKEN)
