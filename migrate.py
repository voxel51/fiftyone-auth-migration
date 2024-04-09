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
    print("Migrating users...")
    async for user in auth0_manager.iter_users():
        await insert_users(dict(user))

    print("Organization migration complete")

async def migrate_organization():
    print("Migrating Organization...")
    org = await auth0_manager.get_organization()
    
    await insert_org(dict(org))

    print("User migration complete")

async def main():
    print("Migrating from Auth0 to Internal...")
    await migrate_organization()
    await migrate_users()

    print("Migration complete")
    print(f"The migrated data can be found in the {Config.CAS_DATABASE} database")

asyncio.run(main())
