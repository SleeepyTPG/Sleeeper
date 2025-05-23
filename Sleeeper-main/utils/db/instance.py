from utils.jsondb import JSONDatabase as json

db = json("db.json")

def create_collections():
    for collection in [
        "afk",
        "marry",
        "logger",
        "levels",
        "levelChannels",
        "verify",
        "warns",
        "warnChannels",
        "warnIds",
    ]:
        db.create_collection(collection)
