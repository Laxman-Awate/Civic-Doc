import motor.motor_asyncio
from .config import settings


client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_uri)
db = client[settings.mongodb_db]


# convenience collections
complaints_col = db.get_collection("complaints")