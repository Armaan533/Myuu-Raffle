import pymongo
import os

current = os.getcwd()
currentFiles = os.listdir(current)
if ".replit" in currentFiles:
    mongoclient = pymongo.MongoClient(os.getenv('mongo_db_link'),serverSelectionTimeoutMs = 5000)

hexdbase = mongoclient["hex_colours"]
colorCollection = hexdbase["colours"]

raffledbase = mongoclient["Raffle_Bot"]
guildpref = raffledbase["Guild Preference"]