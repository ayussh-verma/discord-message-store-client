import os

ENV_VAR_PREFIX = "DISC_MSG_STORE_CLIENT_"


class Config:
    BOT_TOKEN = os.environ[ENV_VAR_PREFIX + "BOT_TOKEN"]
    BOT_GUILD_ID = int(os.environ[ENV_VAR_PREFIX + "BOT_GUILD_ID"])
    API_BASE_URL = os.getenv(ENV_VAR_PREFIX + "API_BASE_URL", "http://localhost:8100")

    API_RETRY_LIMIT = 5
    BOT_PREFIX = "!"
