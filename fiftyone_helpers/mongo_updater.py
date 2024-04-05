import datetime

from config import Config
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(Config.MONGO_URI)

db = client[Config.CAS_DATABASE]

async def insert_org(org_data):
    collection = "orgs"
    org_data["is_default"] = True
    await db[collection].insert_one(org_data)

async def insert_users(user_data):
    collection = "users"
    user = make_cas_user(user_data)
    await db[collection].insert_one(user)

def make_cas_user(user_data):
    # add membership info, shape of user object
    user_data["memberships"] = [
        {
            "groupIds": user_data["group_ids"],
            "joinedAt": datetime.datetime.now(datetime.timezone.utc),
            "orgId": user_data["organization"].id,
            "role": user_data["role"]
        }
    ]
    user_data.pop("organization", None)
    user_data.pop("role", None)
    user_data.pop("group_ids", None)
    return user_data
