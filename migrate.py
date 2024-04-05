"""
| Copyright 2017-2024, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

import asyncio

from auth0_helpers import Auth0ManagementAPIFactory, Auth0Manager
from config import Config
from fiftyone_helpers import insert_org, insert_users

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

async def migrate_users():
    async for user in auth0_manager.iter_users():
        await insert_users(dict(user))

async def migrate_organization():
    org = await auth0_manager.get_organization()
    await insert_org(dict(org))

async def main():
    await migrate_organization()
    await migrate_users()

asyncio.run(main())
