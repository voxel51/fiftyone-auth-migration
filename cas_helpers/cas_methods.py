import aiohttp
from config import Config

CAS_BASE_URL = Config.CAS_BASE_URL
HEADERS = {"X-API-KEY": Config.CAS_AUTH_SECRET}

session = aiohttp.ClientSession()


async def add_org(session, org_data):
    print("Adding Organization...")
    async with session.post(f"{CAS_BASE_URL}/orgs/", headers=HEADERS, data={
            "id": org_data["id"],
            "name": org_data["name"],
            "displayName": org_data["display_name"],
            "pypiToken": org_data["pypi_token"],
            "isDefault": True
            }) as resp:
        ...
    print(f"Added Organization {org_data['name']}")

async def add_user(session, user_data):
    org_id = user_data["organization"].id
    print("Adding User...")
    async with session.post(f"{CAS_BASE_URL}/orgs/{org_id}/users/", headers=HEADERS, data={
            "id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "role": user_data["role"]
            }) as resp:
          print(f"Added User {user_data['email']}")

