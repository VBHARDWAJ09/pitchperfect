from pymongo import MongoClient, errors
import os

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
