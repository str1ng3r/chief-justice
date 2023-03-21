from config import DB_CONN_STRING, DATABASE
import certifi
from motor.motor_asyncio import AsyncIOMotorClient


class DatabaseManagerBase:
    def __init__(self):
        self.ca = certifi.where()
        self.client = AsyncIOMotorClient(DB_CONN_STRING, tlsCAFile=self.ca)
        self.db = self.client[DATABASE]

    async def close(self):
        self.client.close()
