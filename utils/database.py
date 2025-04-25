from pymongo import MongoClient, errors
import os
from bson import ObjectId

db_url = os.getenv("MONGO_URI")
db_connection = None

def connectDB():
    try:
        client = MongoClient(db_url, serverSelectionTimeoutMS=5000)
        database = client["pitchperfectai"]
        client.admin.command('ping')  # Check connection

        return {"database":database, "connected":True}

    except errors.ServerSelectionTimeoutError as err:
        return {"database":None, "connected":False}

    except Exception as e:
        return {"database":None, "connected":False}

def set_db_connection(conn):
    global db_connection
    db_connection = conn

def get_db_connection():
    return db_connection

def save_data(collection,data):
    col = db_connection[collection]
    result = col.insert_one(data)
    return result.inserted_id

def get_data_by_id(collection,id):
    col = db_connection[collection]
    data = col.find_one({'_id': ObjectId(id)})
    if data:
        data['_id'] = str(data['_id'])
    return data


def get_data_by_query(collection, query):
    col = db_connection[collection]

    # Convert _id to ObjectId if needed
    if '_id' in query and isinstance(query['_id'], str):
        try:
            query['_id'] = ObjectId(query['_id'])
        except Exception:
            return None

    results = col.find(query)  # You can change to find() to get multiple documents

    data = [{**doc, '_id': str(doc['_id'])} for doc in results]

    return data