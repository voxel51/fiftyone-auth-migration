"""
| Copyright 2017-2024, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

import aiohttp
import asyncio

from auth0_helpers import Auth0ManagementAPIFactory, Auth0Manager
from config import Config
from cas_helpers import add_org, add_user, get_auth_mode, get_existing_auth_config

auth0_mgmt_factory = Auth0ManagementAPIFactory(
    Config.CLIENT_DOMAIN,
    Config.CLIENT_ID,
    Config.CLIENT_SECRET,
    Config.AUDIENCE,
)

auth0_manager = Auth0Manager(
    Config.ORGANIZATION_ID,
    auth0_mgmt_factory,
)

async def migrate_users(session):
    print("Migrating Users...")
    async for user in auth0_manager.iter_users():
        await add_user(session, dict(user))

async def migrate_organization(session):
    print("Migrating Organizations...")
    org = await auth0_manager.get_organization()
    await add_org(session, dict(org))

async def main():
    async with aiohttp.ClientSession() as session:
        mode = await get_auth_mode(session)

    # test connection to CAS
    if not mode:
        print("==== Error ====")
        print("Unable to connect to the Central Auth Service (CAS)\n")
        print("Please check your Fiftyone Teams deployment and ensure that")
        print("there is a running CAS at the supplied CAS_BASE_URL\n")

    # we don't want to run in legacy mode
    if mode == "legacy":
        print("==== Alert ====")
        print("The migration script must be run using a Central Auth")
        print("Service (CAS) configured to internal mode.\n")
        print("The currently running CAS is configured to legacy mode\n")
        print("Please check the FIFTYONE_AUTH_MODE environment variable")
        print("in your running Fiftyone Teams Deployment\n")
        print("For help, contact your Voxel51 Customer Service Representative\n")

    # it's internal, green light go!
    if mode == "internal":
        async with aiohttp.ClientSession() as session:
            auth_config = await get_existing_auth_config(session)
            await migrate_organization(session)
            await migrate_users(session)
            if not auth_config:
                print("==== Warning ====")
                print("An existing auth configuration was not found")
                print("or does not match an existing IdP configuration.\n")
                print("Please review your auth configuration in the provided")
                print("page at: {your domain}/cas/admins")

        print("Migration Complete")


asyncio.run(main())
