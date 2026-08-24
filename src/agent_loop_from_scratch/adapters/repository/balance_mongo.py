from agent_loop_from_scratch.ports.repository.balance import BalanceNotFound, BalanceModel
from pymongo.collection import Collection
from pymongo import MongoClient
from pymongo.database import Database

class BalanceMongoRepositoryImpl:
    database_name="agent_loop_from_scratch"
    collection_name="balance"

    def __init__(self, mongo_client:MongoClient):
        self.mongo_client = mongo_client
        self.db:Database = self.mongo_client.get_database(self.database_name)
        self.balance_collection:Collection = self.db.get_collection(self.collection_name)
        

    def balance_by_date(self, date_string: str)-> BalanceModel | BalanceNotFound:

        filter={
            'date': date_string
        }
        result = self.balance_collection.find_one(
            filter=filter
        )

        if result is None:
            return BalanceNotFound(
                message="data not found"
            )


        return BalanceModel(id=str(result.get("_id")), date=result.get("date"), amount=result.get("balance"))