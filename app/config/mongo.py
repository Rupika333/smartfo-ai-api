from pymongo import MongoClient

connection_String = "mongodb://localhost:27017"
mclient = MongoClient('localhost',27017)

db = mclient['Charter']

collection_1 = db['accounts']
collection_2 = db['pid']

users= db['users']