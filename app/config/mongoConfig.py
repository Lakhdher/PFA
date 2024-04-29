from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()


def get_db():
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    db = os.getenv('DB_NAME')
    client = MongoClient(host, int(port))
    db_client = client[db]
    return db_client
