# database.py

from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB configuration
client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client.loan_evaluation_db

# Collections
loan_requests_collection = db['loan_requests']
loan_performance_collection = db['loan_performance']
