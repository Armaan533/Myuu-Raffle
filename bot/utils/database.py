import motor.motor_asyncio, os

# connector = pymongo.MongoClient(os.environ.get("mongo_db_link"), serverSelectionTimeoutMs = 5000)
connector = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("mongo_db_link"), serverSelectionTimeoutMs = 5000)

dbase: motor.motor_asyncio.AsyncIOMotorDatabase = connector["Raffle_Bot"]

guildPref: motor.motor_asyncio.AsyncIOMotorCollection = dbase["Guild Preference"]

raffles: motor.motor_asyncio.AsyncIOMotorCollection = dbase["Raffles"]

savior_dbase: motor.motor_asyncio.AsyncIOMotorDatabase = connector["Savior_Database"]


# async def do_find_one(collection: motor.motor_asyncio.AsyncIOMotorCollection, filter: dict):
#     document = await collection.