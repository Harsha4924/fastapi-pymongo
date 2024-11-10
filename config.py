
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from typing import Generator

uri = "mongodb+srv://checkharsha29:password@harsha.kmkra.mongodb.net/?retryWrites=true&w=majority&appName=harsha"





def get_product_collection() -> Generator[Collection, None, None]:
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        yield client['my_db']['myproducts']
    finally:
        client.close()

def get_user_collection() -> Generator[Collection, None, None]:
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        yield client['my_db']['Users']
    finally:
        client.close()