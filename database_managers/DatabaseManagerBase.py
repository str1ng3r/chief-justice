from config import db_password, database
import certifi
from motor.motor_asyncio import AsyncIOMotorClient


class DatabaseManagerBase:
    def __init__(self):
        self.ca = certifi.where()
        self.client = AsyncIOMotorClient(
            f"mongodb+srv://cj-bot:{db_password}@cluster0.itj78.mongodb.net/myFirstDatabase?retryWrites=true&w"
            "=majority", tlsCAFile=self.ca)
        self.db = self.client[database]

    async def close(self):
        self.client.close()
