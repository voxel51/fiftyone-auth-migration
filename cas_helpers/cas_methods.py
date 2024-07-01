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
            "email": user_data["email"].lower(),
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "role": user_data["role"]
            }) as resp:
          print(f"Added User {user_data['email'].lower()}")


async def get_existing_auth_config(session):
    async with session.get(f"{CAS_BASE_URL}/config/", headers=HEADERS) as resp:
        # check if this looks like an auto imported auth0 config
        if resp.status == 200:
            info = await resp.json()
            for provider in info["authenticationProviders"]:
                id = provider["id"]
                org = provider["authorization"]["params"]["organization"]
                # if the id matches our auto generated and the org id
                # matches the existing auth0 org id, this is the
                # associated one created automatically and can be used.
                # otherwise, we  want to warn the user to review
                # their auth config

                # check the auth0 client secret:
                client_secret = provider["clientSecret"]
                if client_secret != Config.CLIENT_SECRET:
                    print("==== Warning ====")
                    print("Please note that the currently configured clientSecret")
                    print("is the management secret. This should be updated to")
                    print("use the auth secret. This can be referenced in the")
                    print("environment variable `AUTH0_CLIENT_SECRET`")
                    print("This value should be updated for users to log in")

                if id == "auth0" and org == Config.ORGANIZATION_ID:
                    return True
        return False

