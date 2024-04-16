"""
| Copyright 2017-2024, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

import aiohttp
import asyncio

from auth0_helpers import Auth0ManagementAPIFactory, Auth0Manager
from config import Config
from cas_helpers import add_org, add_user

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
    session = aiohttp.ClientSession()
    await migrate_organization(session)
    await migrate_users(session)
    await session.close()
    print("Migration Complete")

asyncio.run(main())
