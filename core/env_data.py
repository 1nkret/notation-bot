from dotenv import load_dotenv
from os import getenv

load_dotenv()

token = getenv("BOT_TOKEN")
redis_url = getenv("REDIS_URL", "redis://redis:6379/0")
mongo_url = getenv("MONGO_URL", "mongodb://mongo:27017")
