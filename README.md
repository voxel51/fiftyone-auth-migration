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

Create an environment file, `.env` at the root of the project by copying the `env.template` file.

Copy the relevant values from your Fiftyone Teams deployment `.env` file for docker compose deployments or `values.yaml` file for Kubernetes deployments to the newly created `.env` file in this project.

Set those variables for your current terminal session by running the following from the root of the project:

```
export $(grep -v '^#' .env | xargs)
```

If you have trouble locating these values or the `.env` file for your Fiftyone Teams deployment, please contact your Voxel51 Customer Success representative

After the enviornment variables have been set, you are ready to run the migration script.

Run

```
python migrate.py
```

If needed, the script can be run additional times without duplicating data.

It will always attempt to retrieve all users in the provided Auth0 organization (the ORGANIZATION_ID in `config.py`)
and populate the internal database with the same user information.

Once completed, the specified organization and associated users will be available to use in Fiftyone Teams.
