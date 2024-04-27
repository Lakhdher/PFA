import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_db():
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    db = os.getenv('DB_NAME')
    client = MongoClient(host, int(port))
    db = client[db]
    return db
