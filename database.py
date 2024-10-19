from motor.motor_asyncio import AsyncIOMotorClient

# Connexion à MongoDB Atlas (modifiez l'URL avec vos informations)
client = AsyncIOMotorClient("mongodb+srv://joeazar:Joe!87654321@cluster-joe.zos2odc.mongodb.net/loan-service?retryWrites=true&w=majority")

# Nom de la base de données
db = client['loan-service']  # Base de données : loan-service

# Collections
loan_requests_collection = db['loan_requests']
loan_performance_collection = db['loan_performance']
