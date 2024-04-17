"""
| Copyright 2017-2024, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

import os


class Config:
    # Auth0 config
    AUDIENCE = os.environ["AUTH0_AUDIENCE"]
    CLIENT_DOMAIN = os.environ["AUTH0_DOMAIN"]
    CLIENT_ID = os.environ["AUTH0_MGMT_CLIENT_ID"]
    CLIENT_SECRET = os.environ["AUTH0_MGMT_CLIENT_SECRET"]
    ORGANIZATION_ID = os.environ["AUTH0_ORGANIZATION"]

    # script config
    MAX_HTTP_RETRIES = int(os.environ.get("MAX_HTTP_RETRIES") or 10)

    # CAS config
    CAS_BASE_URL = os.environ["CAS_BASE_URL"]
    FIFTYONE_AUTH_SECRET = os.environ["FIFTYONE_AUTH_SECRET"]

