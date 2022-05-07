import pymongo
import os

mongoclient = pymongo.MongoClient("mongodb://armaan533s:duBE7GLlj6YVAnOH@cluster0-shard-00-00.tw8fv.mongodb.net:27017,cluster0-shard-00-01.tw8fv.mongodb.net:27017,cluster0-shard-00-02.tw8fv.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-1x45s3-shard-0&authSource=admin&retryWrites=true&w=majority",serverSelectionTimeoutMs = 5000)

hexdbase = mongoclient["hex_colours"]
colorCollection = hexdbase["colours"]

raffledbase = mongoclient["Raffle_Bot"]
guildpref = raffledbase["Guild Preference"]