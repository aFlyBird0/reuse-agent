from pymongo import MongoClient
from pymongo.server_api import ServerApi

def _get_default_db():
    # TODO: seceret
    uri = "mongodb+srv://aflybird0:8ORG2lDRRm36ntP7@cluster0.lh2vpp8.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    # print(self.client.list_databases())
    db = client["cluster0"]
    return db


default_db = _get_default_db()
