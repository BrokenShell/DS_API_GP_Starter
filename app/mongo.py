from typing import Dict, List, Optional
from os import getenv

from MonsterLab import Monster
from dotenv import load_dotenv
from pandas import DataFrame
from pymongo import MongoClient


class MongoDB:
    load_dotenv()

    def __init__(self):
        self.db_url = getenv("MONGODB_URL")
        self.database = MongoClient(self.db_url)["MonsterLab"]
        self.collection = self.database["Monsters"]

    def create(self, data: List[Dict]):
        self.collection.insert_many(data)

    def read(self, query: Optional[Dict] = None) -> List[Dict]:
        return list(self.collection.find(query or {}, {"_id": False}))

    def update(self, query: Dict, update_data: Dict):
        self.collection.update_one(query, {"$set": update_data})

    def delete(self, query: Dict):
        self.collection.delete_many(query)

    def count(self, query: Optional[Dict] = None) -> int:
        return self.collection.count_documents(query or {})

    def dataframe(self, query: Optional[Dict] = None) -> DataFrame:
        return DataFrame(self.read(query or {}))

    def seed(self, amount: int):
        self.create([Monster().to_dict() for _ in range(amount)])

    def info(self):
        return {
            "Platform": "MongoDB",
            "Database": self.database.name,
            "Collection": self.collection.name,
            "Size": f"{self.count()} Monsters",
        }
