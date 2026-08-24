"""
One-off script to seed the MongoDB 'balance' collection
with data from BalanceDicRepository.balances
"""
import os
import dotenv
from pymongo import MongoClient
from agent_loop_from_scratch.adapters.repository.balance_dict import BalanceDicRepository

dotenv.load_dotenv()

client = MongoClient(os.getenv("MONGO_DB_URI"))
db = client.get_database("agent_loop_from_scratch")
collection = db.get_collection("balance")

# Convert the dict into a list of documents
documents = [
    {"date": date_str, "balance": amount}
    for date_str, amount in BalanceDicRepository.balances.items()
]

result = collection.insert_many(documents)
print(f"Inserted {len(result.inserted_ids)} documents into 'balance' collection.")

client.close()
