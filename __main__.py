import os

from utils import Megumin
from naff import Intents
from dotenv import load_dotenv

load_dotenv()
client = Megumin(intents=Intents.ALL)
token = os.getenv("TOKEN")

if __name__ == "__main__":
    client.start(token)
