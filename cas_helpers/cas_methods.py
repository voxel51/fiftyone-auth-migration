import aiohttp
from config import Config

CAS_BASE_URL = Config.CAS_BASE_URL
HEADERS = {"X-API-KEY": Config.FIFTYONE_AUTH_SECRET}


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

async def get_auth_mode(session):
    try:
        async with session.get(f"{CAS_BASE_URL}/config/mode/", headers=HEADERS) as resp:
            if resp.status != 200:
                return None

            auth_mode = await resp.json()
            return auth_mode["mode"]
    except aiohttp.client_exceptions.ClientConnectorError as e:
        print("Unable to connect to CAS with ERROR: ", e, "\n")
        return None

