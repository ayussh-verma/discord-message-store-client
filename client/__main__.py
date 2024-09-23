from client.bot import BOT

import os

from client.config import Config

from loguru import logger

with logger.catch(message="Unexpected error", level="CRITICAL", reraise=True):
    BOT.run(Config.BOT_TOKEN)
