# NOTE: This repository is currently under construction
---
# Fiftyone Teams Auth Migration Script

## Intent

This tool is provided to help users move from the Legacy auth environments of Fiftyone Teams to the Internal environment.

Specifically, it helps facilitate moving organizations and users from an existing Auth0 Tenant to the Internal ecosystem so that user and role information can be preserved.

## Usage

This script is designed to be used with a running version of Fiftyone Teams version >= 1.6.0

For the script to run properly, the `FIFTYONE_AUTH_MODE` environment variable in the Fiftyone Teams deployment must be set to the value `internal`.



Using python>=3.10, install requirements from the root:

```
pip install -r requirements.txt
```

Populate the values of the `config.py` file at the root. These values can be found in your Fiftyone Teams deployment. If you need help finding these files, please contact your Voxel51 Customer Success representative.

Run

```
python migrate.py
```

If needed, the script can be run additional times without duplicating data.

It will always attempt to retrieve all users in the provided Auth0 organization (the ORGANIZATION_ID in `config.py`)
and populate the internal database with the same user information.

Once completed, the specified organization and associated users will be available to use in Fiftyone Teams.

