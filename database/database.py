import pymongo
import os

MONGO_URI = os.getenv('MONGO_URI')

client = pymongo.MongoClient(MONGO_URI)
db = client['Eventual']

eventos = db['Eventos']
logs = db['Logs']

print("Database connected")